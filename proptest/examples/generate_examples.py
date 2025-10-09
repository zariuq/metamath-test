#!/usr/bin/env python3
"""
Generate example randomized Metamath databases for demonstration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generators.template_substitutor import parse_template, randomized_symbol_mapper, substitute_template
from runners.metamath_runner import verify_metamath


def generate_examples(template_path, num_examples=3):
    """Generate multiple randomized versions of a template."""

    template_name = os.path.basename(template_path)
    print(f"\n{'='*80}")
    print(f"Template: {template_name}")
    print(f"{'='*80}\n")

    # Read template
    with open(template_path, 'r') as f:
        template_content = f.read()

    # Show original
    print("ORIGINAL TEMPLATE:")
    print("-" * 80)
    print(template_content[:500])
    if len(template_content) > 500:
        print(f"\n... [{len(template_content)} total characters] ...\n")
    print("-" * 80)

    # Parse
    constants, variables, labels, typecodes = parse_template(template_content)
    print(f"\nParsed elements:")
    print(f"  Constants: {sorted(constants)[:10]}" + (" ..." if len(constants) > 10 else ""))
    print(f"  Variables: {sorted(variables)}")
    print(f"  Labels: {sorted(labels)[:10]}" + (" ..." if len(labels) > 10 else ""))
    print(f"  Typecodes: {sorted(typecodes)}")

    # Generate examples
    for i in range(num_examples):
        print(f"\n{'─'*80}")
        print(f"RANDOMIZED EXAMPLE #{i+1}")
        print(f"{'─'*80}")

        # Generate mapper
        mapper = randomized_symbol_mapper(constants, variables, labels, typecodes).example()

        # Show some mappings
        print("\nSample mappings:")
        for const in sorted(list(constants)[:5]):
            print(f"  {const:15s} → {mapper.get_constant(const)}")
        for var in sorted(list(variables)[:5]):
            print(f"  {var:15s} → {mapper.get_variable(var)}")
        for lbl in sorted(list(labels)[:5]):
            print(f"  {lbl:15s} → {mapper.get_label(lbl)}")

        # Substitute
        randomized = substitute_template(template_content, mapper)

        print("\nRandomized output:")
        print("-" * 80)
        print(randomized[:600])
        if len(randomized) > 600:
            print(f"\n... [{len(randomized)} total characters] ...")
        print("-" * 80)

        # Verify
        print("\nVerification:")
        result = verify_metamath(randomized)
        if result.success:
            print("  ✅ PASS - Valid Metamath database!")
        else:
            print(f"  ❌ FAIL - {result.error_message}")

        # Save to file
        output_path = f"example_{template_name.replace('.mm', '')}_{i+1}.mm"
        with open(output_path, 'w') as f:
            f.write(randomized)
        print(f"  Saved to: {output_path}")


if __name__ == '__main__':
    # Demo with demo0.mm
    demo0_path = '/home/zar/claude/hyperon/metamath/metamath-test/demo0.mm'

    if os.path.exists(demo0_path):
        generate_examples(demo0_path, num_examples=3)
    else:
        print(f"Template not found: {demo0_path}")

    # Demo with anatomy.mm
    anatomy_path = '/home/zar/claude/hyperon/metamath/tests/anatomy.mm'
    if os.path.exists(anatomy_path):
        generate_examples(anatomy_path, num_examples=2)
