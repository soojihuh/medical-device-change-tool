"""
Quick smoke test for the assessment & document generation pipeline.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from assessor_fda import assess_fda
from assessor_hc import assess_hc
from assessor_eu import assess_eu
from doc_fda import build_fda_document
from doc_hc import build_hc_document
from doc_eu import build_eu_document


def test():
    print("🧪 Running smoke tests...\n")

    config_path = Path(__file__).parent / "example_config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    product_info = config["productInfo"]
    change_info = config["changeInfo"]
    metadata = config["metadata"]
    auto_answers = config["autoAnswers"]

    # ===== Test 1: Non-significant for all countries =====
    print("Test 1: Non-significant change scenario")
    fda_result = assess_fda(auto_answers["FDA"], change_info)
    hc_result = assess_hc(auto_answers["HC"], change_info)
    eu_result = assess_eu(auto_answers["EU"], change_info)

    print(f"  FDA: {'⚠️  Significant' if fda_result['isSignificant'] else '✅ Not Significant'} - {fda_result['requiredAction']}")
    print(f"  HC : {'⚠️  Significant' if hc_result['isSignificant'] else '✅ Not Significant'} - {hc_result['requiredAction']}")
    print(f"  EU : {'⚠️  Significant' if eu_result['isSignificant'] else '✅ Not Significant'} - {eu_result['requiredAction']}")

    assert not fda_result["isSignificant"], "Test 1 FAILED: FDA should be Not Significant"
    assert not hc_result["isSignificant"], "Test 1 FAILED: HC should be Not Significant"
    assert not eu_result["isSignificant"], "Test 1 FAILED: EU should be Not Significant"
    print("  ✅ PASSED\n")

    # ===== Test 2: Significant scenario =====
    print("Test 2: Significant change scenario (new patient population described)")
    sig_fda = dict(auto_answers["FDA"])
    sig_fda["A1"] = True       # change in indications for use statement
    sig_fda["A1.1"] = False    # not single-use -> reusable
    sig_fda["A1.2"] = False    # not Rx -> OTC
    sig_fda["A1.3"] = False    # not just a name/readability change
    sig_fda["A1.4"] = True     # describes a new disease/condition/patient population
    sig_result = assess_fda(sig_fda, change_info)
    assert sig_result["isSignificant"], "Test 2 FAILED: A1.4=true should be Significant"
    print(f"  FDA with new patient population described: {sig_result['requiredAction']}")
    print("  ✅ PASSED\n")

    # ===== Test 2b: EU significant scenario =====
    print("Test 2b: EU significant change scenario (extension of intended purpose)")
    sig_eu = dict(auto_answers["EU"])
    sig_eu["MAIN_A"] = True  # change of intended purpose
    sig_eu["A1"] = False     # not a limitation
    sig_eu["A2"] = True      # extension of intended purpose
    non_detector_change_info = dict(change_info)
    non_detector_change_info["componentName"] = "Control Unit"  # avoid the NB detector exception
    sig_eu_result = assess_eu(sig_eu, non_detector_change_info)
    assert sig_eu_result["isSignificant"], "Test 2b FAILED: A2=true (extension) should be Significant"
    print(f"  EU with intended purpose extension: {sig_eu_result['requiredAction']}")
    print("  ✅ PASSED\n")

    # ===== Test 2c: HC significant scenario =====
    print("Test 2c: HC significant change scenario (control mechanism change)")
    sig_hc = dict(auto_answers["HC"])
    sig_hc["G_DESIGN"] = True
    sig_hc["D1"] = True  # control mechanism / operating principle change
    sig_hc_result = assess_hc(sig_hc, change_info)
    assert sig_hc_result["isSignificant"], "Test 2c FAILED: D1=true should be Significant"
    print(f"  HC with control mechanism change: {sig_hc_result['requiredAction']}")
    print("  ✅ PASSED\n")

    # ===== Test 3: Document generation =====
    print("Test 3: Document generation")
    doc_meta = dict(metadata)
    doc_meta["docNumber"] = f"{metadata['docNumberPrefix']}-TEST"

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)

    docs = [
        ("FDA_TEST.docx", build_fda_document(product_info, change_info, fda_result, doc_meta)),
        ("HC_TEST.docx",  build_hc_document(product_info, change_info, hc_result, doc_meta)),
        ("EU_TEST.docx",  build_eu_document(product_info, change_info, eu_result, doc_meta)),
    ]

    for name, doc in docs:
        out_path = out_dir / name
        doc.save(str(out_path))
        size_kb = out_path.stat().st_size / 1024
        print(f"  📄 {name} → {size_kb:.1f} KB")
    print("  ✅ PASSED\n")

    print("🎉 All tests passed!")


if __name__ == "__main__":
    try:
        test()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
