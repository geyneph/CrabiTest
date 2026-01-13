# Crabi Test

## Project Overview
This project was developed as part of a technical data analytics case for **Crabi**, an insurance company.  
The objective is to evaluate technical capabilities in **data cleaning, analysis, and visualization**, as well as the ability to extract **business insights** related to claims, services, loss ratio (siniestralidad), and severity.

The analysis focuses on understanding claims behavior, costs, and risk patterns throughout the lifecycle of an insurance policy.

---

##  Objectives
The main goals of this analysis are:

- Calculate the **monthly loss ratio (siniestralidad)** of the company
- Identify the **coverage with the highest and lowest number of claims**
- Determine the **partner with the highest and lowest loss ratio**
- Calculate **average severity** by partner
- Analyze claims distribution by **age range** of insured users
- Build a **Python-based, reproducible analysis pipeline**
- Provide **visual insights** through dashboards and charts

---

## 📂Data Sources
The project uses the following datasets provided by Crabi:

- `claim.xlsx` – Historical record of insurance claims
- `service.xlsx` – Services and actions associated with each claim
- `people.xlsx` – Insured users demographic information
- `status.xlsx`
- `status_type.xlsx`
- `status_cause.xlsx`
- `Diccionario de Datos.xlsx` – Data dictionary and field definitions

⚠️ **Important Rule**:  
Source files must **not be modified**. All cleaning and transformations are done programmatically to ensure the solution recalculates correctly if data changes.

---

## 🧠 Key Concepts Used

### Reserves
Funds set aside to cover future costs related to insurance claims (repairs, medical expenses, logistics, etc.).

### Loss Ratio (Siniestralidad)
The relationship between:
- **Total claim expenses in a given month**
- **Total earned premiums in the same month**

Assumption:
- Monthly earned premiums = **200,000 MXN**

### Severity
The total cost of a claim **after applying deductibles**, calculated as:

