import json
import os
import sys

# Add parent directory to path to import rag
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag import generate_answer

def run_eval():
    with open("eval/test_questions.json", "r") as f:
        questions = json.load(f)
        
    total = len(questions)
    abstentions = 0
    correct_abstentions = 0
    citation_correct = 0
    
    print(f"Starting evaluation of {total} questions...\n")
    
    for idx, q in enumerate(questions):
        print(f"Q{idx+1}: {q['query']}")
        res = generate_answer(q["query"], q["jurisdiction"])
        answer = res["answer"]
        citations = res["citations"]
        confidence = res["confidence"]
        
        is_abstention = "do not have sufficient context" in answer or confidence == "Low"
        
        if is_abstention:
            abstentions += 1
            if q["expected_type"] == "out_of_scope":
                correct_abstentions += 1
        
        # Citation correctness check:
        # We ensure every citation generated was actually in the retrieved docs
        retrieved_sources = [f"{d['metadata'].get('source_name', '')} - {d['metadata'].get('section', '')}" for d in res["docs"]]
        citations_valid = True
        for cit in citations:
            if cit not in retrieved_sources:
                citations_valid = False
                break
                
        if citations_valid and not is_abstention:
            citation_correct += 1
            
        print(f"  Expected: {q['expected_type']}, Abstention: {is_abstention}, Citations Valid: {citations_valid}")
        print(f"  Confidence: {confidence}")
        
    in_scope_total = len([q for q in questions if q["expected_type"] == "in_scope"])
    out_scope_total = len([q for q in questions if q["expected_type"] == "out_of_scope"])
    
    abstention_rate = (correct_abstentions / out_scope_total) * 100 if out_scope_total else 0
    citation_accuracy = (citation_correct / in_scope_total) * 100 if in_scope_total else 0
    
    print("\n--- Evaluation Results ---")
    print(f"Total Questions: {total}")
    print(f"Out-of-Scope Correct Abstention Rate: {abstention_rate}% ({correct_abstentions}/{out_scope_total})")
    print(f"In-Scope Citation Correctness: {citation_accuracy}% ({citation_correct}/{in_scope_total})")
    print(f"Overall Abstentions (includes low confidence on in-scope): {abstentions}")

if __name__ == "__main__":
    run_eval()
