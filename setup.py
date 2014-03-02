from distutils.core import setup

setup(
        name='ledDriver',
        version='1.0',
        description='Python LED light strip and PWM drivers using the WiringPi2 library.',
        author='Cameron Little',
        author_email='cameron@camlittle.com',
        url='https://github.com/apexskier/ledDriver',
        py_modules=['ledDriver', 'pwmDriver']
    )
