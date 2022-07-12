from hsrr_processor.tests.test_changes_model import createChangesModel
from hsrr_processor.models import drop_runs_command

m = createChangesModel()
c = drop_runs_command.dropRunsCommand(runs=['M621 EB CL2'],routeModel = m,runInfoModel=None)