# Copyright (c) 2009, Jacob Kragh
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials
#    provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from commands.module import Module
from libraries.core import get_config, put_config
from lxml import etree
from string import Template
from templates.controller import controller

class Controller:
    def __init__(self, superclass=None, router=None):
        """Initialize the controller by storing information about the
        module to which it belongs and by passing along run-time
        arguments to the configure method.

        Args:
            superclass: Full name of the controller's superclass,
                        e.g., "Mage_Adminhtml_Controller_Action".
            router: Name of the front controller router to use.
                    Available routers are "standard", "admin", and
                    "default".

        """
        self.module = Module().identify()
        self._configure(superclass, router)

    def _configure(self, superclass, router):
        """Store the controller's superclass and router."""
        default = "Mage_Core_Controller_Front_Action"
        self.superclass = superclass if superclass else default
        self.router = router if router else "standard"

    def create(self, name):
        """Create the controller.

        Dispatch requests to create an empty controller class and
        update the module's configuration file.

        Args:
            name: Name of the controller with or without the
                  "Controller" suffix, e.g., "IndexController"
                  or "Tracking".

        """
        suffix = "controller"
        if name.lower().endswith(suffix):
            name = name[:-len(suffix)]
        self.name = name.capitalize() + "Controller"
        self.front_name = self.module["name"].lower()

        self._create_class()
        self._update_config()

    def _create_class(self):
        """Create an empty controller class."""
        template = Template(controller)
        template = template.substitute(namespace=self.module["namespace"],
                                       module_name=self.module["name"],
                                       controller_name=self.name,
                                       superclass=self.superclass)
        dest = open("controllers/%s.php" % self.name, "w")
        dest.write(template)
        dest.close()

    def _update_config(self):
        """Make Mage aware that this module has controllers to dispatch to.
        
        Update the module's configuration file to configure a route,
        which will allow Mage to dispatch requests to the module's
        controller(s).

        """
        config = get_config()
        frontend = config.find("frontend")
        if config.xpath("/config/frontend"):
            if config.xpath("/config/frontend/routers"):
                return # Assume that a route has already been configured.
        else:
            frontend = etree.SubElement(config, "frontend")

        # Now we're sure frontend exists, so we
        # can add child elements to it.
        routers = etree.SubElement(frontend, "routers")
        module_name_lower = etree.SubElement(routers, self.front_name)
        use = etree.SubElement(module_name_lower, "use")
        use.text = self.router
        args = etree.SubElement(module_name_lower, "args")
        module = etree.SubElement(args, "module")
        module.text = "%s_%s" % (self.module["namespace"], self.module["name"])
        front_name = etree.SubElement(args, "frontName")
        front_name.text = self.front_name

        put_config(config)
