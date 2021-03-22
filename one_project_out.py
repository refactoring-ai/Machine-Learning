import copy
from os import path
from pathlib import Path

import joblib

from binary_classification import run
from configs import RESULTS_DIR_PATH
from utils import date_utils
from utils.log import log_close, log_init

if __name__ == "__main__":
    log_init(
        path.join(
            RESULTS_DIR_PATH,
            "log",
            f"classifier_training_{date_utils.windows_path_friendly_now()}.txt"))
    projects = [
        'MaintenanceAPI',
        'AgreementPreferencesAPI',
        'AgreementsOverviewNLAPI',
        'mobile_backend',
        'EnrollmentAPI',
        'mobile-components',
        'paymentsapi',
        'mobile_tools',
        'security-proxy',
        'authentication-api',
        'registration-api',
        'ExperienceComponents',
        'authorization-api',
        'monitoring',
        'security-gateway',
        'contactless-payment-cards-api',
        'gMobileActivationWA',
        'cardmanagementapi',
    ]
    t = {}
    for project in projects:
        for project_to_leave_out in projects:
            if project != project_to_leave_out:
                one_out = copy.copy(projects)
                one_out.remove(project_to_leave_out)
                print(f'leaving out {project_to_leave_out}')
                print(f'including {one_out}')
                x = run(one_out, [project_to_leave_out])
                t[project_to_leave_out] = x
    joblib.dump(t, path.join(Path.home(), "Machine-Learning/one_out.joblib"))
    log_close()
