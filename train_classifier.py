"""Train the supervised resume/job match classifier.

Expected CSV columns: resume_text, job_description, label
Example labels: Strong Match, Moderate Match, Poor Match
"""

import argparse
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from classifier import ResumeJobClassifier


def train_model(data_path: str, model_path: str) -> None:
    data = pd.read_csv(data_path).dropna(
        subset=["resume_text", "job_description", "label"]
    )
    required = {"resume_text", "job_description", "label"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if data["label"].nunique() < 2:
        raise ValueError("Training data must contain at least two label classes.")

    train_data, test_data = train_test_split(
        data,
        test_size=0.2,
        random_state=42,
        stratify=data["label"],
    )

    classifier = ResumeJobClassifier()
    classifier.train(
        train_data["resume_text"],
        train_data["job_description"],
        train_data["label"],
    )

    predictions = [
        classifier.predict(resume, job)["label"]
        for resume, job in zip(test_data["resume_text"], test_data["job_description"])
    ]
    print(f"Accuracy: {accuracy_score(test_data['label'], predictions):.3f}")
    print(classification_report(test_data["label"], predictions, zero_division=0))

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    classifier.save(model_path)
    print(f"Model saved to {model_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/resume_job_labels.csv")
    parser.add_argument("--model", default="models/resume_classifier.joblib")
    args = parser.parse_args()
    train_model(args.data, args.model)


if __name__ == "__main__":
    main()
