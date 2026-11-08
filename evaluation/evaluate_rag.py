
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from app.rag.policy_rag import PolicyRAG


TEST_CASES = [
    ("Can I return an unused product?", "returns.txt"),
    ("How many days do I have to return an item?", "returns.txt"),
    ("When will I receive my refund?", "refunds.txt"),
    ("How do refunds work?", "refunds.txt"),
    ("Can I cancel my order?", "cancellations.txt"),
    ("What are the shipping charges?", "shipping.txt"),
    ("How long does delivery take?", "delivery.txt"),
    ("What if my product arrives damaged?", "damaged_items.txt"),
    ("What should I do if an item is missing?", "missing_items.txt"),
    ("What payment methods are accepted?", "payments.txt"),
    ("Is cash on delivery available?", "cod.txt"),
    ("Can I exchange a product?", "exchanges.txt"),
    ("How is my personal information protected?", "privacy.txt"),
    ("How can I escalate an unresolved complaint?", "escalation.txt"),
    ("Can I return a hygiene-sensitive product?", "returns.txt"),
]


def evaluate_strategy(rag, strategy):
    rows = []

    for number, (question, expected_source) in enumerate(
        TEST_CASES, start=1
    ):
        start = time.perf_counter()

        results = rag.search(
            question,
            strategy=strategy,
            limit=3,
        )

        latency_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        retrieved_sources = [
            item["source"] for item in results
        ]

        hit_at_1 = int(
            bool(retrieved_sources)
            and retrieved_sources[0] == expected_source
        )

        hit_at_3 = int(
            expected_source in retrieved_sources[:3]
        )

        rows.append({
            "query_id": number,
            "strategy": strategy,
            "question": question,
            "expected_source": expected_source,
            "top_source": (
                retrieved_sources[0]
                if retrieved_sources else ""
            ),
            "retrieved_sources": " | ".join(
                retrieved_sources
            ),
            "hit_at_1": hit_at_1,
            "hit_at_3": hit_at_3,
            "latency_ms": latency_ms,
        })

        print(
            f"[{strategy}] Query {number:02d}: "
            f"Hit@1={hit_at_1}, "
            f"Hit@3={hit_at_3}, "
            f"{latency_ms} ms"
        )

    return rows


def main():
    output_dir = Path("evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)

    rag = PolicyRAG()
    index_info = rag.build_index()

    print("Index:", index_info)
    print()

    all_rows = []

    for strategy in ("full", "chunks"):
        all_rows.extend(
            evaluate_strategy(rag, strategy)
        )

    summary = {
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_queries": len(TEST_CASES),
        "index": index_info,
        "results": {},
    }

    for strategy in ("full", "chunks"):
        rows = [
            row for row in all_rows
            if row["strategy"] == strategy
        ]

        count = len(rows)

        summary["results"][strategy] = {
            "hit_at_1": round(
                sum(row["hit_at_1"] for row in rows) / count,
                4,
            ),
            "hit_at_3": round(
                sum(row["hit_at_3"] for row in rows) / count,
                4,
            ),
            "average_latency_ms": round(
                sum(row["latency_ms"] for row in rows) / count,
                2,
            ),
        }

    csv_path = output_dir / "rag_evaluation_results.csv"
    json_path = output_dir / "rag_evaluation_summary.json"

    with csv_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(all_rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(all_rows)

    json_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("\n===== EVALUATION SUMMARY =====")

    for strategy, metrics in summary["results"].items():
        print(f"\nStrategy: {strategy}")
        print(f"Hit@1: {metrics['hit_at_1']:.2%}")
        print(f"Hit@3: {metrics['hit_at_3']:.2%}")
        print(
            "Average latency: "
            f"{metrics['average_latency_ms']} ms"
        )

    print("\nSaved:")
    print(csv_path)
    print(json_path)


if __name__ == "__main__":
    main()
