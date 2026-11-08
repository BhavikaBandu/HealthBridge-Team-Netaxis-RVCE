# HealthBridge — Demo Video

**▶ Watch the demo video:** [Google Drive folder](https://drive.google.com/drive/folders/1fHM1TJb_3J6om1189Yb6z32ErhwMCkEG?usp=sharing)

## About the video

The video walks through both portals using a synthetic scenario, a patient travelling from India to the UAE, that
highlights 8 different cases: 3 medicines, 2 procedures and 3 documents (lab report, referral and prescription). The
same flow works for other routes as well (for example UAE to Switzerland). All patient data shown is synthetic.

## Portal features

**Patient portal**
- Medical history: medicines, conditions, procedures and allergies
- Documents: upload lab reports, prescriptions and referrals (values are read automatically)
- My Trips: plan a trip and its destination
- Travel Health Summary: what each record means at the destination, with sources, and a printable report in English or Arabic
- Doctor Access: choose which doctors can see the records

**Doctor portal**
- Patient Records: invite a patient by Patient ID and view their records once access is granted
- Finding cards: a comparison for each medicine, procedure and document, with a Dopamine–Cortisol confidence score
- Flags: destination rules and documents the patient needs
- Complete patient report in English or Arabic
- Knowledge Explorer: search the official sources directly

## Demo case: India to UAE

- **Medicine Agent:** Crocin Advance 500 mg and Augmentin DUO were matched to UAE equivalents (Panadol Advance 500 mg,
  Augmentin 1 g) with the same ingredients. A check found no reaction with ibuprofen, to which the patient is allergic.
- **Procedure Agent:** A knee MRI was matched to a 3T MRI service in Dubai.
- **Report Agent:** Glucose 108 mg/dL was converted to 5.99 mmol/L and creatinine 0.78 mg/dL to 68.95 µmol/L, the units
  used in the UAE. The prescription was checked for missing details.
- **Policy Agent:** Tramadol 50 mg is controlled in the UAE, and sources disagreed on prior approval. The patient was
  told to get approval before travelling and to carry the prescription.

**Confidence and Dopamine–Cortisol:** Augmentin and the lab report scored the highest Dopamine (1.0 and 0.97) with low
Cortisol (0.03 and 0.12). The knee MRI was a Medium-confidence match (Dopamine 0.74, Cortisol 0.39), because the UAE
service covers joints in general rather than the knee specifically.
