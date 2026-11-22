import pathlib
import yaml

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render


DEMONSTRATION_ARTIFACTS_PATH = pathlib.Path(settings.BASE_DIR).parent.parent / 'verification_artifacts' / 'demonstration'


def load_procedure(procedure_name: str) -> dict:
    """Load a procedure YAML file.
    
    Args:
        procedure_name (str): The name of the procedure YAML file (without the .yaml extension).

    Returns:
        Data from the procedure YAML file.
    """
    procedure_name = procedure_name.removesuffix('.yaml')
    yaml_file = DEMONSTRATION_ARTIFACTS_PATH / f"{procedure_name}.yaml"

    with open(yaml_file, 'r', encoding='utf-8') as f:
        procedure_data = yaml.safe_load(f) or {}

    return procedure_data


def vaildate_procedure(procedure_name: str, procedure_data: dict):
    """Validate a procedure YAML file before rendering it.

    Args: 
        procedure_name (str): The name of the procedure YAML file (without the .yaml extension).
        procedure_data (dict): Data from a procedure YAML file.
    
    Returns:
        True if valid procedure. representing the validity of the procedure. If false, 
        error message will be provided. 
    """
    REQUIRED_PROCEDURE_FIELDS = {'id', 'title', 'acceptance_criteria_ids', 'steps'}
    REQUIRED_STEP_FIELDS = {'id', 'type', 'description', 'expected_result'}

    missing_fields = sorted(REQUIRED_PROCEDURE_FIELDS - set(procedure_data.keys()))
    if missing_fields:
        error_message = (
            f"Procedure '{procedure_name}' is missing required fields: {', '.join(missing_fields)}."
        )
        return error_message
       
    steps = procedure_data.get('steps', [])
    if not isinstance(steps, list) or not steps:
        error_message = (f"Procedure '{procedure_name}' does not contain any steps.")
        return error_message

    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            error_message = (f"Step {index} in '{procedure_name}' is invalid.")
            return error_message

        missing_step_fields = sorted(REQUIRED_STEP_FIELDS - set(step.keys()))
        if missing_step_fields:
            error_message = (
                "Procedure '{procedure_name}' step {index} is missing required fields: {fields}".format(
                    procedure_name=procedure_name,
                    index=index,
                    fields=', '.join(missing_step_fields),
                )
            )
            return error_message


def verification_home(request):
    """Renders the verification home page."""
    return render(request, 'verification/verification.html')


def select_procedure(request):
    """Renders the page with a list of available procedures."""
    if request.method == 'POST':
        procedure_name = request.POST.get('selected_procedure')
        if procedure_name:
            procedure_name = procedure_name.removesuffix('.yaml')
            return redirect('procedure_preconditions', procedure_name=procedure_name)

    procedures = [f.name.removesuffix('.yaml') for f in DEMONSTRATION_ARTIFACTS_PATH.iterdir() if f.is_file()]
    context = {
        'procedures': sorted(procedures),
    }
    return render(request, 'verification/procedures.html', context)


def procedure_steps(request, procedure_name: str, step_number: int = None):
    """Renders the steps page for a specific procedure."""
    procedure_name = procedure_name.removesuffix('.yaml')
    procedure = load_procedure(procedure_name)
    vaildate_procedure(procedure_name, procedure)

    preconditions = procedure.get("preconditions", [])
    steps = procedure.get("steps", [])
    if not step_number:
        step_number = 1

    step_index = int(step_number) - 1
    if step_index < 0 or step_index >= len(steps):
        raise Http404("Step not found")

    current_step = steps[step_index]
    prev_step = step_index if step_index > 0 else None
    next_step = step_index + 2 if step_index < len(steps) - 1 else None

    context = {
        "procedure": procedure,
        "procedure_name": procedure_name,
        "procedure_title": procedure.get('title', procedure_name),
        "preconditions": preconditions,
        "step": current_step,
        "step_number": step_index + 1,
        "total_steps": len(steps),
        "prev_step": prev_step,
        "next_step": next_step,
    }
    return render(request, "verification/procedure_steps.html", context)


def procedure_preconditions(request, procedure_name: str):
    """Renders the preconditions page for a specific procedure."""
    procedure_name = procedure_name.removesuffix('.yaml')
    procedure = load_procedure(procedure_name)
    error = vaildate_procedure(procedure_name, procedure)

    if error:
        messages.error(request, error)
        return redirect('procedures')

    preconditions = procedure.get("preconditions", [])

    if not preconditions:
        return redirect('procedure_step', procedure_name=procedure_name, step_number=1)
    
    context = {
        "procedure": procedure,
        "procedure_name": procedure_name,
        "procedure_title": procedure.get('title', procedure_name),
        "preconditions": preconditions,
    }
    return render(request, "verification/procedure_preconditions.html", context)


def verification_results(request):
    """Renders the verification results page."""
    return render(request, 'verification/results.html')