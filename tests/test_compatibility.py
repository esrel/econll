from sklearn.metrics import classification_report as sklearn_report
from seqeval.metrics import classification_report as seqeval_report
from econll import evaluate


def test_compatibility(conll_refs, conll_hyps):
    # econll report
    evaluate(conll_refs, conll_hyps)

    # scikit-learn report
    print("Sklearn Classification Report")
    print(sklearn_report([tag for block in conll_refs for tag in block],
                         [tag for block in conll_hyps for tag in block],
                         digits=4))

    # seqeval report
    print("Seqeval Classification Report")
    print(seqeval_report(conll_refs, conll_hyps, digits=4))
