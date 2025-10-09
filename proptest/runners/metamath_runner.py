"""
Runners for executing Metamath verifiers on generated test files.

Supports:
- metamath.exe (reference C implementation)
- mmverify.py (Python verifier)
- Additional verifiers can be added
"""

import subprocess
import tempfile
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class VerificationResult:
    """Result of running a verifier on a database."""
    success: bool
    stdout: str
    stderr: str
    returncode: int
    verifier: str
    error_message: Optional[str] = None


def verify_metamath(mm_content: str, timeout: int = 30) -> VerificationResult:
    """
    Verify Metamath database using metamath.exe via mmexe.sh script.

    Args:
        mm_content: String content of .mm file
        timeout: Maximum execution time in seconds

    Returns:
        VerificationResult with success status and output
    """
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mm', delete=False) as f:
        f.write(mm_content)
        temp_path = f.name

    try:
        # Use the mmexe.sh script for proper command formatting
        mmexe_script = '/home/zar/claude/hyperon/metamath/metamath-test/proptest/mmexe.sh'

        result = subprocess.run(
            ['bash', mmexe_script, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # mmexe.sh returns 0 on success, non-zero on failure
        # It also checks for "FAILED" in output
        success = (result.returncode == 0)

        error_msg = None
        if not success:
            # Extract error message
            for line in result.stdout.split('\n'):
                if '?Error' in line or 'error' in line.lower() or 'FAILED' in line:
                    error_msg = line.strip()
                    break

        return VerificationResult(
            success=success,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            verifier='metamath',
            error_message=error_msg
        )

    except subprocess.TimeoutExpired:
        return VerificationResult(
            success=False,
            stdout='',
            stderr=f'Timeout after {timeout}s',
            returncode=-1,
            verifier='metamath',
            error_message=f'Verification timeout after {timeout}s'
        )
    except Exception as e:
        return VerificationResult(
            success=False,
            stdout='',
            stderr=str(e),
            returncode=-1,
            verifier='metamath',
            error_message=f'Runner error: {e}'
        )
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass


def verify_mmverify(mm_content: str, timeout: int = 30) -> VerificationResult:
    """
    Verify Metamath database using mmverify.py.

    Args:
        mm_content: String content of .mm file
        timeout: Maximum execution time in seconds

    Returns:
        VerificationResult with success status and output
    """
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mm', delete=False) as f:
        f.write(mm_content)
        temp_path = f.name

    try:
        mmverify_path = '/home/zar/claude/hyperon/metamath/mmverify/mmverify.py'

        result = subprocess.run(
            ['python3', mmverify_path, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # mmverify.py returns 0 on success
        success = result.returncode == 0

        error_msg = None
        if not success:
            # Extract error from stderr
            if result.stderr:
                error_msg = result.stderr.split('\n')[0]

        return VerificationResult(
            success=success,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            verifier='mmverify',
            error_message=error_msg
        )

    except subprocess.TimeoutExpired:
        return VerificationResult(
            success=False,
            stdout='',
            stderr=f'Timeout after {timeout}s',
            returncode=-1,
            verifier='mmverify',
            error_message=f'Verification timeout after {timeout}s'
        )
    except Exception as e:
        return VerificationResult(
            success=False,
            stdout='',
            stderr=str(e),
            returncode=-1,
            verifier='mmverify',
            error_message=f'Runner error: {e}'
        )
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass


def verify_all(mm_content: str, timeout: int = 30) -> dict:
    """
    Run all available verifiers and return results.

    Args:
        mm_content: String content of .mm file
        timeout: Maximum execution time per verifier

    Returns:
        Dict mapping verifier name to VerificationResult
    """
    results = {}

    # Run metamath
    results['metamath'] = verify_metamath(mm_content, timeout)

    # Run mmverify.py
    results['mmverify'] = verify_mmverify(mm_content, timeout)

    return results


if __name__ == '__main__':
    # Test with demo0.mm
    demo0_path = '/home/zar/claude/hyperon/metamath/metamath-test/demo0.mm'

    print("Testing verifiers with demo0.mm...\n")

    with open(demo0_path, 'r') as f:
        demo0_content = f.read()

    results = verify_all(demo0_content)

    for verifier, result in results.items():
        print(f"{verifier}: {'✓ PASS' if result.success else '✗ FAIL'}")
        if result.error_message:
            print(f"  Error: {result.error_message}")

    # Test with invalid content
    print("\n\nTesting with invalid content...\n")
    bad_content = "$c term $.\n$v x $.\nbad $a term x $."

    results = verify_all(bad_content)

    for verifier, result in results.items():
        print(f"{verifier}: {'✓ PASS' if result.success else '✗ FAIL'}")
        if result.error_message:
            print(f"  Error: {result.error_message}")
