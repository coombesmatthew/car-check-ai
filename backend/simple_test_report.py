#!/usr/bin/env python3
"""Simple EA11OSE AI report generation test using Anthropic API directly."""

import json
import os
from pathlib import Path

import anthropic

# Load .env file manually
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key not in os.environ:
                    os.environ[key] = value

# Load test data
fixture_path = Path(__file__).parent / "fixtures" / "EA11OSE_FULL_CHECK.json"
with open(fixture_path) as f:
    check_data = json.load(f)

# Initialize Anthropic client
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)

# Create a context message for the report
context = f"""
Generate a comprehensive buyer's report for the following vehicle:

Registration: EA11 OSE
Make: MINI
Model: Cooper D Convertible
Year: 2011
Fuel: Diesel
Body: Convertible
Transmission: Manual 6 Gear
Engine: 1598cc
CO2: 105 g/km
Colour: Black
Seats: 4

Registration Date: 2011-04-20 (age: 14.94 years)
Current Mileage: 100,440 miles (6,725 mi/year avg)
Tax Status: Taxed (£20/year, Pre-April 2017 rates)
MOT Status: Valid until 2026-09-29
Previous Keepers: 1

MOT History:
- Total tests: 14
- Passed: 11
- Failed: 3
- Latest: PASSED 2025-09-30
- Advisories: 3

Valuation (Brego):
- Private sale: £2,272 - £3,212
- Trade: £774 - £1,513

Provenance:
- Finance: None outstanding
- Stolen: No
- Write-off: No
- Salvage: None found

Provide a detailed buyer's report covering:
1. Overall condition assessment
2. Value analysis
3. Risk factors
4. Maintenance predictions
5. Negotiation tips
6. Running costs (tax, insurance, maintenance)
"""

print("Calling Anthropic API to generate EA11OSE report...")
print("=" * 60)

try:
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": context
            }
        ]
    )

    report = message.content[0].text

    # Save the report
    output_path = Path(__file__).parent / "EA11OSE_REPORT.md"
    with open(output_path, "w") as f:
        f.write(report)

    print(report)
    print("=" * 60)
    print(f"\n✓ Report saved to: {output_path}")
    print(f"Tokens used: {message.usage.input_tokens} input + {message.usage.output_tokens} output")

except anthropic.APIError as e:
    print(f"ERROR: {e}")
    exit(1)
