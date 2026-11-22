import pathlib

from verification_framework.apps.verification import views


def test_load_procedure():
    procedure_name = 'valid_procedure'
    data_path = pathlib.Path(__file__).resolve().parents[1] / 'data'
    procedure = views.load_procedure(procedure_name, data_path)

    assert isinstance(procedure, dict)