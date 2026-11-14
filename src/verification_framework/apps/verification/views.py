import pathlib
import yaml

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render


DEMONSTRATION_ARTIFACTS_PATH = pathlib.Path(settings.BASE_DIR).parent.parent / 'verification_artifacts' / 'demonstration'
REQUIRED_PROCEDURE_FIELDS = {'id', 'title', 'steps'}
REQUIRED_STEP_FIELDS = {'id', 'type', 'description', 'expected_result'}


def load_procedure_data(procedure_name):
    """Load and validate a procedure YAML file before rendering it."""
    procedure_name = procedure_name.removesuffix('.yaml')
    yaml_file = DEMONSTRATION_ARTIFACTS_PATH / f"{procedure_name}.yaml"
    if not yaml_file.exists():
        raise Http404("Procedure not found")

    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            procedure = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        raise Http404(f"Invalid YAML for procedure '{procedure_name}': {exc}") from exc

    missing_fields = sorted(REQUIRED_PROCEDURE_FIELDS - set(procedure.keys()))
    if missing_fields:
        raise Http404(
            f"Procedure '{procedure_name}' is missing required fields: {', '.join(missing_fields)}"
        )

    steps = procedure.get('steps', [])
    if not isinstance(steps, list) or not steps:
        raise Http404(f"Procedure '{procedure_name}' does not contain any steps.")

    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise Http404(f"Step {index} in '{procedure_name}' is invalid.")

        missing_step_fields = sorted(REQUIRED_STEP_FIELDS - set(step.keys()))
        if missing_step_fields:
            raise Http404(
                "Procedure '{procedure_name}' step {index} is missing required fields: {fields}".format(
                    procedure_name=procedure_name,
                    index=index,
                    fields=', '.join(missing_step_fields),
                )
            )

    return procedure


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


def procedure_steps(request, procedure_name, step_number=None):
    """Renders the steps page for a specific procedure."""
    procedure_name = procedure_name.removesuffix('.yaml')
    procedure = load_procedure_data(procedure_name)

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


def procedure_preconditions(request, procedure_name):
    """Renders the preconditions page for a specific procedure."""
    procedure_name = procedure_name.removesuffix('.yaml')
    procedure = load_procedure_data(procedure_name)

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