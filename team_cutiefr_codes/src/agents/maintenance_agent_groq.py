# ============================================================
# src/agents/maintenance_agent_groq.py
# ReflectAI AI Maintenance Agent — Groq Edition
#
# Uses Groq SDK (pip install groq)
# API key format: gsk_xxxxxxxxxxxxxxxxxxxxxxxx
# Get key at: https://console.groq.com
#
# Model: llama-3.1-8b-instant (lightweight, high free-tier limits)
# ============================================================

import os
import json
import datetime
from typing import List, Dict, Any

from groq import Groq

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ── IRC Thresholds (mcd·lx⁻¹·m⁻²) ──────────────────────────
RA_THRESHOLDS = {
    "Lane Centreline Marking": 80,
    "Edge Lane Marking":       80,
    "Road Stud / RPM":         150,
    "Shoulder Sign":           250,
    "Gantry Sign":             250,
    "Delineator":              100,
}

# Repair cost estimates (INR per unit / per 10m stretch)
REPAIR_COSTS = {
    "Lane Centreline Marking": 500,
    "Edge Lane Marking":       400,
    "Road Stud / RPM":         800,
    "Shoulder Sign":           15000,
    "Gantry Sign":             50000,
    "Delineator":              1200,
}

# ── Groq model (supports tool calling) ──────────────────────
GROQ_MODEL = "llama-3.1-8b-instant"


# ============================================================
# Tool implementations (executed locally, called by Groq)
# ============================================================

def analyze_scan_results(scan_data: str) -> str:
    """Parse scan results JSON and identify non-compliant sections."""
    try:
        results = json.loads(scan_data)
    except json.JSONDecodeError:
        return "Error: Invalid scan data JSON"

    detections = (
        results.get("detections", results)
        if isinstance(results, dict)
        else results
    )
    if not isinstance(detections, list):
        detections = [detections] if isinstance(detections, dict) else []

    compliant     = []
    warning       = []
    non_compliant = []

    highway_section = (
        results.get("highway_section", "Unknown Section")
        if isinstance(results, dict) else "Unknown Section"
    )
    scan_date = (
        results.get("scan_date", datetime.date.today().isoformat())
        if isinstance(results, dict) else datetime.date.today().isoformat()
    )

    for det in detections:
        if not isinstance(det, dict):
            continue
        element_type = det.get("element_type", "Unknown")
        ra_score     = float(det.get("ra_score", 0))
        threshold    = RA_THRESHOLDS.get(element_type, 80)
        status       = det.get("status", "")

        if not status:
            if ra_score >= threshold:
                status = "COMPLIANT"
            elif ra_score >= threshold * 0.75:
                status = "WARNING"
            else:
                status = "NON-COMPLIANT"

        entry = {
            "element_type": element_type,
            "ra_score":     ra_score,
            "threshold":    threshold,
            "deficit":      round(threshold - ra_score, 1),
            "gps":          det.get("gps", det.get("location", "GPS not recorded")),
            "confidence":   det.get("confidence", 0.0),
        }

        if status == "COMPLIANT":
            compliant.append(entry)
        elif status == "WARNING":
            warning.append(entry)
        else:
            non_compliant.append(entry)

    summary = (
        f"\nSCAN ANALYSIS SUMMARY\n"
        f"Highway Section: {highway_section}\n"
        f"Scan Date:       {scan_date}\n"
        f"Total Elements:  {len(detections)}\n\n"
        f"COMPLIANCE BREAKDOWN:\n"
        f"  Compliant:     {len(compliant)} elements\n"
        f"  Warning:       {len(warning)} elements\n"
        f"  Non-Compliant: {len(non_compliant)} elements\n\n"
        f"NON-COMPLIANT ELEMENTS (require immediate action):\n"
    )

    for item in non_compliant:
        summary += (
            f"\n  * {item['element_type']}\n"
            f"    RA Score: {item['ra_score']} mcd/lx/m2  (IRC Minimum: {item['threshold']})\n"
            f"    Deficit:  {item['deficit']} mcd/lx/m2 below standard\n"
            f"    Location: {item['gps']}\n"
        )

    if warning:
        summary += "\nWARNING ELEMENTS (schedule within 30 days):\n"
        for item in warning:
            summary += (
                f"  * {item['element_type']} at {item['gps']}"
                f" -- RA: {item['ra_score']} (threshold: {item['threshold']})\n"
            )

    return summary


def prioritize_maintenance(issues: str) -> str:
    """Prioritize maintenance tasks by safety criticality."""
    tier1_cost = sum(
        REPAIR_COSTS.get(k, 1000)
        for k in ["Road Stud / RPM", "Lane Centreline Marking"]
        for _ in range(3)
    )
    tier3_cost = sum(
        REPAIR_COSTS.get(k, 1000)
        for k in ["Edge Lane Marking", "Shoulder Sign"]
        for _ in range(2)
    )

    return (
        "\nPRIORITIZED MAINTENANCE PLAN\n"
        "============================================================\n\n"
        "TIER 1 -- URGENT (Complete within 7 days):\n"
        "  Elements: Road Studs/RPMs, Lane Centreline Markings with >50% RA deficit\n"
        "  Reason:   Direct night-time safety risk; IRC non-compliance\n"
        "  Action:   Issue emergency work order; deploy maintenance crew immediately\n\n"
        "TIER 2 -- HIGH PRIORITY (Complete within 14 days):\n"
        "  Elements: Edge Lane Markings, Delineators with any IRC deficit\n"
        "  Reason:   Night visibility degradation; potential accident risk\n"
        "  Action:   Schedule maintenance crew; procure retroreflective materials\n\n"
        "TIER 3 -- SCHEDULED (Complete within 30 days):\n"
        "  Elements: Signs and markings in WARNING range (75-100% of IRC minimum)\n"
        "  Reason:   Approaching non-compliance; proactive maintenance more cost-effective\n"
        "  Action:   Include in next scheduled maintenance run\n\n"
        f"COST ESTIMATE:\n"
        f"  Emergency repair (Tier 1+2): INR {tier1_cost:,} estimated\n"
        f"  Preventive maintenance (Tier 3): INR {tier3_cost:,} estimated\n\n"
        "NOTE: Actual costs depend on stretch length and contractor rates.\n"
    )


def estimate_repair_cost(element_types_json: str) -> str:
    """Estimate repair cost for non-compliant elements."""
    try:
        data = json.loads(element_types_json) if isinstance(element_types_json, str) else {}
    except Exception:
        data = {}

    lines = ["REPAIR COST ESTIMATE", "=" * 40, ""]
    total = 0

    for element_type, cost_per_unit in REPAIR_COSTS.items():
        quantity     = data.get(element_type, 1)
        element_cost = cost_per_unit * quantity
        total       += element_cost
        lines.append(f"{element_type}:")
        lines.append(f"  Quantity:  {quantity} units/10m stretches")
        lines.append(f"  Unit Cost: INR {cost_per_unit:,}")
        lines.append(f"  Total:     INR {element_cost:,}")
        lines.append("")

    lines.append(f"TOTAL ESTIMATED COST: INR {total:,}")
    lines.append("")
    lines.append("Note: Includes material + labour. Excludes traffic management costs.")
    return "\n".join(lines)


def generate_work_order(priority_list: str, highway_section: str) -> str:
    """Generate a formal NHAI maintenance work order."""
    work_order_id = (
        f"NHAI-WO-{datetime.date.today().strftime('%Y%m%d')}"
        f"-{abs(hash(highway_section)) % 10000:04d}"
    )
    today         = datetime.date.today().strftime("%d %B %Y")
    due_urgent    = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%d %B %Y")
    due_scheduled = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%d %B %Y")

    return (
        "\n"
        "================================================================================\n"
        "NATIONAL HIGHWAYS AUTHORITY OF INDIA\n"
        "RETROREFLECTIVITY MAINTENANCE WORK ORDER\n"
        "================================================================================\n"
        f"Work Order ID:     {work_order_id}\n"
        f"Issue Date:        {today}\n"
        f"Highway Section:   {highway_section}\n"
        "Generated By:      ReflectAI AI-Powered Assessment System (Groq Edition)\n"
        "Standard:          IRC 67:2012 (Signs), IRC 35:2015 (Markings)\n"
        "================================================================================\n\n"
        "AUTHORISATION\n"
        "This work order is issued under NHAI O&M contract provisions for retroreflectivity\n"
        "maintenance. The contractor must commence Tier 1 works within 72 hours of receipt\n"
        "and complete all listed elements by the dates specified.\n\n"
        "SCOPE OF WORK\n"
        f"{priority_list}\n\n"
        "DUE DATES\n"
        f"  Tier 1 (Urgent):    Complete by {due_urgent}\n"
        f"  Tier 2 (Priority):  Complete by {due_urgent}\n"
        f"  Tier 3 (Scheduled): Complete by {due_scheduled}\n\n"
        "COMPLIANCE REQUIREMENT\n"
        "All repaired elements must meet IRC 67:2012 / IRC 35:2015 minimum RA values.\n"
        "Post-repair retroreflectometer readings must be submitted within 48 hours.\n\n"
        "CONTACT\n"
        "Regional Maintenance Officer, NHAI\n"
        "Email: maintenance@nhai.gov.in\n\n"
        "================================================================================\n"
        "Generated automatically by ReflectAI\n"
        "AI-Powered Retroreflectivity Measurement System -- Groq LLaMA Edition\n"
        "================================================================================\n"
    )


# ── Tool dispatcher ──────────────────────────────────────────
TOOL_FUNCTIONS = {
    "analyze_scan_results":   analyze_scan_results,
    "prioritize_maintenance": prioritize_maintenance,
    "estimate_repair_cost":   estimate_repair_cost,
    "generate_work_order":    generate_work_order,
}

SYSTEM_PROMPT = (
    "You are a helpful road maintenance assistant. "
    "Read the analysis data below and write a clear, easy-to-understand maintenance report. "
    "Use simple words that anyone can understand. Avoid technical jargon. "
    "Include: what was found, what needs fixing, how urgent it is, estimated cost, "
    "and a formal work order section at the end."
)


# ============================================================
# Main agent function (runs tools locally, uses Groq for summary)
# ============================================================

def run_maintenance_agent(
    scan_results,
    highway_section: str = "Unknown Section",
    max_iterations: int = 12,
    verbose: bool = True
) -> str:
    """
    Run the ReflectAI Groq AI maintenance agent.

    Runs all analysis tools locally first, then uses Groq LLaMA
    to generate a simple, human-readable summary report.

    Args:
        scan_results:     list or dict of detection results from ReflectAI
        highway_section:  highway section identifier string
        max_iterations:   unused (kept for API compatibility)
        verbose:          print intermediate steps to console

    Returns:
        Final maintenance report as string
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return (
            "Error: GROQ_API_KEY not set.\n"
            "Set it with: export GROQ_API_KEY=gsk_your_key_here\n"
            "Get a free key at: https://console.groq.com"
        )

    client = Groq(api_key=api_key)

    # ── Step 1: Run all tools locally ────────────────────────
    scan_json = json.dumps({
        "highway_section": highway_section,
        "scan_date":        datetime.date.today().isoformat(),
        "detections": (
            scan_results
            if isinstance(scan_results, list)
            else scan_results.get("detections", [scan_results])
        )
    }, default=str)

    if verbose:
        print("[Agent] Step 1: Analyzing scan results...")
    analysis = analyze_scan_results(scan_json)

    if verbose:
        print("[Agent] Step 2: Prioritizing maintenance...")
    priorities = prioritize_maintenance(analysis)

    if verbose:
        print("[Agent] Step 3: Estimating repair costs...")
    costs = estimate_repair_cost("{}")

    if verbose:
        print("[Agent] Step 4: Generating work order...")
    work_order = generate_work_order(priorities, highway_section)

    # ── Step 2: Combine all results ──────────────────────────
    combined_data = (
        f"=== SCAN ANALYSIS ===\n{analysis}\n\n"
        f"=== PRIORITY PLAN ===\n{priorities}\n\n"
        f"=== COST ESTIMATE ===\n{costs}\n\n"
        f"=== WORK ORDER ===\n{work_order}"
    )

    # ── Step 3: Ask Groq to write a simple summary ───────────
    if verbose:
        print("[Agent] Step 5: Asking Groq AI to write simple summary...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Here is the full maintenance analysis for {highway_section}. "
                f"Please rewrite this as a clear, simple report that anyone can understand.\n\n"
                f"{combined_data}"
            )
        }
    ]

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=1500,
            temperature=0.3,
        )
        ai_summary = response.choices[0].message.content or ""
    except Exception as api_err:
        err_str = str(api_err)
        if verbose:
            print(f"[Agent] Groq API error: {err_str}")
        # If Groq fails, return the raw combined data as fallback
        ai_summary = ""

    # ── Build final report ───────────────────────────────────
    if ai_summary.strip():
        final_report = (
            f"{'=' * 60}\n"
            f"REFLECTAI MAINTENANCE REPORT\n"
            f"Highway: {highway_section}\n"
            f"Date: {datetime.date.today().strftime('%d %B %Y')}\n"
            f"{'=' * 60}\n\n"
            f"{ai_summary}\n\n"
            f"{'=' * 60}\n"
            f"DETAILED WORK ORDER\n"
            f"{'=' * 60}\n"
            f"{work_order}"
        )
    else:
        # Fallback if Groq call fails — return raw analysis
        final_report = (
            f"{'=' * 60}\n"
            f"REFLECTAI MAINTENANCE REPORT\n"
            f"Highway: {highway_section}\n"
            f"Date: {datetime.date.today().strftime('%d %B %Y')}\n"
            f"{'=' * 60}\n\n"
            f"{combined_data}"
        )

    if verbose:
        print("[Agent] Done!")

    return final_report


# ============================================================
# PDF Report Generator (optional, requires fpdf2)
# ============================================================

def generate_pdf_report(
    work_order_text: str,
    highway_section: str,
    output_path: str = "outputs/maintenance_report.pdf"
) -> str:
    """Generate a PDF maintenance report from work order text."""
    if not PDF_AVAILABLE:
        return "fpdf2 not installed. Run: pip install fpdf2"

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    pdf = FPDF()
    pdf.add_page()

    # Header bar
    pdf.set_fill_color(0, 70, 127)
    pdf.set_text_color(255, 255, 255)
    pdf.rect(0, 0, 210, 25, "F")
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_y(8)
    pdf.cell(0, 10, "NHAI -- ReflectAI Maintenance Report (Groq Edition)", align="C")
    pdf.ln(20)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Highway Section: {highway_section}", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Generated: {datetime.datetime.now().strftime('%d %B %Y %H:%M')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Courier", size=9)
    for line in work_order_text.split("\n"):
        # Safely encode non-latin chars
        safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
        pdf.cell(0, 5, safe_line[:105], ln=True)

    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(
        0, 5,
        "Generated by ReflectAI  |  Powered by Groq LLaMA  |  6th NHAI Innovation Hackathon",
        align="C"
    )

    pdf.output(output_path)
    return output_path


# ============================================================
# Demo scan data
# ============================================================

DEMO_SCAN_RESULTS = [
    {"element_type": "Lane Centreline Marking", "ra_score": 85.0,  "status": "COMPLIANT",     "confidence": 0.92, "gps": "28.6139N, 77.2090E"},
    {"element_type": "Edge Lane Marking",        "ra_score": 55.0,  "status": "WARNING",       "confidence": 0.88, "gps": "28.6142N, 77.2091E"},
    {"element_type": "Road Stud / RPM",          "ra_score": 32.0,  "status": "NON-COMPLIANT", "confidence": 0.95, "gps": "28.6145N, 77.2093E"},
    {"element_type": "Shoulder Sign",            "ra_score": 320.0, "status": "COMPLIANT",     "confidence": 0.97, "gps": "28.6148N, 77.2095E"},
    {"element_type": "Gantry Sign",              "ra_score": 190.0, "status": "WARNING",       "confidence": 0.90, "gps": "28.6150N, 77.2097E"},
]


if __name__ == "__main__":
    print("=== ReflectAI Maintenance Agent (Groq Edition) ===\n")
    print("Running Groq LLaMA agent on demo scan results...\n")

    report = run_maintenance_agent(
        scan_results=DEMO_SCAN_RESULTS,
        highway_section="NH-48 Km 120-180 (Delhi-Gurugram)",
        verbose=True
    )

    print("\n" + "=" * 60)
    print("FINAL GROQ AGENT REPORT:")
    print("=" * 60)
    print(report)

    os.makedirs("outputs", exist_ok=True)
    pdf_path = generate_pdf_report(
        report, "NH-48 Km 120-180", "outputs/maintenance_report.pdf"
    )
    if "not installed" not in pdf_path:
        print(f"\nPDF saved to: {pdf_path}")
