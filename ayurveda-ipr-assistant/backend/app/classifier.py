from typing import List, Dict, Optional

class FormulationClassifier:
    def __init__(self):
        # We model this as a simple decision tree.
        # Each node is either a question or a final classification.
        self.tree = {
            "id": "q1",
            "text": "Is the formulation exactly as described in authoritative classical Ayurveda texts (e.g., Ayurvedic Pharmacopoeia of India)?",
            "options": [
                {"label": "Yes, it is identical", "next": "c_classical"},
                {"label": "No, it's a new combination, format, or extract", "next": "q2"}
            ]
        }
        
        self.nodes = {
            "q1": self.tree,
            "q2": {
                "id": "q2",
                "text": "Does it contain exclusively classical Ayurveda ingredients (no modern chemicals/synthetics) but in a novel ratio, dosage form, or combination?",
                "options": [
                    {"label": "Yes, purely classical ingredients but novel combination", "next": "c_proprietary"},
                    {"label": "No, it involves advanced extraction, food usage, or cosmetic use", "next": "q3"}
                ]
            },
            "q3": {
                "id": "q3",
                "text": "What is the primary intended use or extraction method?",
                "options": [
                    {"label": "Highly purified plant extract (phytopharmaceutical) for medical use", "next": "c_phyto"},
                    {"label": "Dietary supplement or food (Ayurveda-Aahar)", "next": "c_aahar"},
                    {"label": "Topical application for beauty/cleansing", "next": "c_cosmetic"},
                    {"label": "Entirely new drug with non-classical active principles", "next": "c_new_drug"}
                ]
            },
            
            # Classifications
            "c_classical": {
                "id": "c_classical",
                "type": "classification",
                "category": "Classical/Generic Medicine",
                "explanation": (
                    "**IP & ABS Posture:**\n"
                    "- **Patentability:** Not patentable in India due to Section 3(p) of the Patents Act (traditional knowledge bar).\n"
                    "- **Prior Art:** Likely documented in the Traditional Knowledge Digital Library (TKDL).\n"
                    "- **ABS (Access & Benefit Sharing):** If you are a foreign entity or using it for commercial research, Biological Diversity Act compliance is required.\n"
                    "👉 *Tip:* Please check the TKDL portal to confirm prior art before filing any IP claims internationally."
                )
            },
            "c_proprietary": {
                "id": "c_proprietary",
                "type": "classification",
                "category": "Proprietary/Patent Medicine (Ayurvedic)",
                "explanation": (
                    "**IP & ABS Posture:**\n"
                    "- **Patentability:** Difficult but possible if you can prove synergistic effect under Section 3(e). Mere admixture is barred.\n"
                    "- **ABS:** Commercial utilization of Indian biological resources triggers Access & Benefit Sharing obligations under the Biological Diversity Act.\n"
                    "- **Trademarks:** Brand names can be protected."
                )
            },
            "c_phyto": {
                "id": "c_phyto",
                "type": "classification",
                "category": "Phytopharmaceutical",
                "explanation": (
                    "**IP & ABS Posture:**\n"
                    "- **Patentability:** Patentable if novel, non-obvious, and industrially applicable. Requires rigorous clinical evidence.\n"
                    "- **Regulatory:** Governed under a separate schedule of the Drugs & Cosmetics Act.\n"
                    "- **ABS:** Strict ABS compliance required under the BD Act for resource access."
                )
            },
            "c_aahar": {
                "id": "c_aahar",
                "type": "classification",
                "category": "Ayurveda-Aahar / Nutraceutical",
                "explanation": (
                    "**IP & ABS Posture:**\n"
                    "- **Patentability:** Generally barred under Section 3(e) unless there's a demonstrable synergistic technical effect. Often protected as trade secrets or via Trademarks.\n"
                    "- **Regulatory:** Regulated by FSSAI under Ayurveda Aahar regulations, not as a drug."
                )
            },
            "c_cosmetic": {
                "id": "c_cosmetic",
                "type": "classification",
                "category": "Cosmetic",
                "explanation": (
                    "**IP & ABS Posture:**\n"
                    "- **Patentability:** Formulations can be patented if they show surprising technical effects (e.g., novel stabilization).\n"
                    "- **Regulatory:** Needs cosmetic manufacturing licenses; cannot claim to 'cure' diseases under the Drugs and Magic Remedies Act."
                )
            },
            "c_new_drug": {
                "id": "c_new_drug",
                "type": "classification",
                "category": "New / Non-Classical Drug",
                "explanation": (
                    "**IP & ABS Posture:**\n"
                    "- **Patentability:** Patentable subject to novelty and inventive step (avoiding Section 3(d) unless significant enhancement in efficacy is shown).\n"
                    "- **Regulatory:** Requires full clinical trials as a new chemical/biological entity."
                )
            }
        }

    def get_node(self, node_id: str) -> Dict:
        return self.nodes.get(node_id)

    def start(self) -> Dict:
        return self.nodes["q1"]
