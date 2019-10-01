#!/usr/bin/env python3

# Copyright 2019 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Encapsulate ceilometer-agent testing."""

import logging

import zaza.openstack.utilities.openstack as openstack_utils
import zaza.openstack.charm_tests.test_utils as test_utils


class CeilometerAgentTest(test_utils.OpenStackBaseTest):
    """Encapsulate ceilometer-agent tests."""

    CONF_FILE = '/etc/ceilometer/ceilometer.conf'

    XENIAL_PIKE = openstack_utils.get_os_release('xenial_pike')
    XENIAL_OCATA = openstack_utils.get_os_release('xenial_ocata')
    XENIAL_NEWTON = openstack_utils.get_os_release('xenial_newton')
    TRUSTY_MITAKA = openstack_utils.get_os_release('trusty_mitaka')
    TRUSTY_LIBERTY = openstack_utils.get_os_release('trusty_liberty')

    @classmethod
    def setUpClass(cls):
        """Run class setup for running ceilometer-agent tests."""
        super(CeilometerAgentTest, cls).setUpClass()

    @property
    def services(self):
        """Return a list services for Openstack Release."""
        current_release = openstack_utils.get_os_release()
        services = []

        if current_release >= CeilometerAgentTest.XENIAL_PIKE:
            services.append('ceilometer-polling: AgentManager worker(0)')
            services.append(
                'ceilometer-agent-notification: NotificationService worker(0)')
        elif current_release >= CeilometerAgentTest.XENIAL_OCATA:
            services.append('ceilometer-collector: CollectorService worker(0)')
            services.append('ceilometer-polling: AgentManager worker(0)')
            services.append(
                'ceilometer-agent-notification: NotificationService worker(0)')
            services.append('apache2')
        elif current_release >= CeilometerAgentTest.XENIAL_NEWTON:
            services.append('ceilometer-collector - CollectorService(0)')
            services.append('ceilometer-polling - AgentManager(0)')
            services.append(
                'ceilometer-agent-notification - NotificationService(0)')
            services.append('ceilometer-api')
        else:
            services.append('ceilometer-collector')
            services.append('ceilometer-api')
            services.append('ceilometer-agent-notification')

            if current_release < CeilometerAgentTest.TRUSTY_MITAKA:
                services.append('ceilometer-alarm-notifier')
                services.append('ceilometer-alarm-evaluator')

            if current_release >= CeilometerAgentTest.TRUSTY_LIBERTY:
                # Liberty and later
                services.append('ceilometer-polling')
            else:
                # Juno and earlier
                services.append('ceilometer-agent-central')

        return services

    # NOTE(beisner): need to add more functional tests

    def test_900_restart_on_config_change(self):
        """Checking restart happens on config change."""
        # Expected default and alternate values
        current_value = openstack_utils.get_application_config_option(
            'ceilometer', 'debug'
        )
        assert type(current_value) == bool
        new_value = not current_value

        # Convert bool to str
        current_value = str(current_value)
        new_value = str(new_value)

        set_default = {'debug': current_value}
        set_alternate = {'debug': new_value}
        default_entry = {'DEFAULT': {'debug': [current_value]}}
        alternate_entry = {'DEFAULT': {'debug': [new_value]}}

        logging.info('changing config: {}'.format(set_alternate))
        self.restart_on_changed(
            CeilometerAgentTest.CONF_FILE,
            set_default,
            set_alternate,
            default_entry,
            alternate_entry,
            self.services)

    def test_901_pause_resume(self):
        """Run pause and resume tests.

        Pause service and check services are stopped then resume and check
        they are started.
        """
        with self.pause_resume(self.services):
            logging.info("Testing pause and resume")
