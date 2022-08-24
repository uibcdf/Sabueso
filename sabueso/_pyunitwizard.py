# Configure PyUnitWizard

import pyunitwizard

pyunitwizard.configure.set_default_form('pint')
pyunitwizard.configure.set_default_parser('pint')
pyunitwizard.configure.set_standard_units(['nm', 'ps', 'K', 'mole', 'amu', 'e',
    'kJ/mol', 'kJ/(mol*nm**2)', 'N', 'degrees'])

