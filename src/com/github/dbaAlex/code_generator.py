__author__ = 'coty'

import logging
from settings import etlunit_config, console
import os


class CodeGenerator():
    """
        This class performs the generation of the code. Using the jinja2 template engine, we are taking in yaml
        and generating code from it by filling in templates.
    """

    # TODO: Determine if the array passed into the class is a single yaml array or if it is multile arrays from files
    def __init__(self, out_dir, data):
        self.log = logging.getLogger(name='CodeGenerator')
        self.log.setLevel(etlunit_config['logging_level'])
        self.log.addHandler(console)

        self.file_ext = '.py'

        self.yaml_data = data
        self.out_dir = out_dir

    def generateCode(self):
        """
            Generate code has to be smart enough to determine if the json array should generate a test case, or a
            fixture or if it needs to generate both.

            * If setup or teardown is present, then its a test case
            * If parent is present, then it needs to extend a fixture
        """
        #TODO: Maybe we should have a yaml validation class?
        #Totaly agree - that makes perfect sense.
        from jinja2 import Environment, FileSystemLoader
        from time import strftime, gmtime

        # TODO: Find a more efficient way to pull in this template other than ../
        # Is is possible to parameterize the template directory?  It should be a static location... - Alex
        # Maybe we can use the PackageLoader
        out_path = "%s/../../../../templates/" % os.path.dirname(os.path.abspath(__file__))
        j2_env = Environment(loader=FileSystemLoader(out_path), trim_blocks=True)

        for yml in self.yaml_data.keys():
            self.log.info("Generating code from %s..." % yml)
            self.yml_data = self.yaml_data[yml]

            try:
                if self.yml_data['fixture'] is not None:
                    self.fixture = self.yml_data['fixture']
                    self.template_output = j2_env.get_template("testfixture.jj2")\
                        .render(create_date=strftime("%a, %d %b %Y %X +0000", gmtime()),
                                fixture=self.fixture)
            except KeyError:
                self.fixture = "unittest.TestCase"  # Default value for fixture
                self.log.info("Fixture not present, generating TestSuite...")
            finally:
                self.template_output = j2_env.get_template("testsuite.jj2") \
                    .render(create_date=strftime("%a, %d %b %Y %X +0000", gmtime()),
                            fixture=self.fixture,
                            tests=self.yml_data['tests'])

            self.persist_output(self.yml_data, self.template_output)
        self.log.info("Code generation complete.")

    def persist_output(self, yml, output):
        # TODO: Decide if naming the files based on the test name from the yaml is ok
        with open("%s/%s%s" % (self.out_dir, str(yml['name']).replace(' ', ''), self.file_ext), 'w') as f:
            os.chmod(f.name, 0770)

            f.write(output)
            f.close()
