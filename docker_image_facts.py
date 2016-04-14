#!/usr/bin/python
#
# Copyright 2016 Red Hat | Ansible
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


from ansible.module_utils.docker_common import *

try:
    from docker import utils
except ImportError:
    # missing docker-py handled in ansible.module_utils.docker
    pass

DOCUMENTATION = '''
---
module: docker_image_facts

short_description: Inspect docker images

description:
     - Provide one or more image names, and the module will inspect each, returning an array of inspection results.

options:
  name:
    description:
      - Image name. Name format will be name:tag or repository/name:tag, where tag is optional. If a tag is not
        provided, 'latest' will be used.
    default: null
    required: true


requirements:
  - "python >= 2.6"
  - "docker-py"

authors:
  - Chris Houseknecht (house@redhat.com)

'''

EXAMPLES = '''

- name: Inspect a single image
  docker_image_facts:
    name: pacur/centos-7

- name: Inspect multiple images
  docker_iamge_facts:
    name:
      - pacur/centos-7
      - sinatra
'''

RETURNS = '''
{
    "changed": false,
    "check_mode": false,
    "results": [
        {
            "Architecture": "amd64",
            "Author": "",
            "Comment": "",
            "Config": {
                "AttachStderr": false,
                "AttachStdin": false,
                "AttachStdout": false,
                "Cmd": [
                    "/etc/docker/registry/config.yml"
                ],
                "Domainname": "",
                "Entrypoint": [
                    "/bin/registry"
                ],
                "Env": [
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                ],
                "ExposedPorts": {
                    "5000/tcp": {}
                },
                "Hostname": "e5c68db50333",
                "Image": "c72dce2618dc8f7b794d2b2c2b1e64e0205ead5befc294f8111da23bd6a2c799",
                "Labels": {},
                "OnBuild": [],
                "OpenStdin": false,
                "StdinOnce": false,
                "Tty": false,
                "User": "",
                "Volumes": {
                    "/var/lib/registry": {}
                },
                "WorkingDir": ""
            },
            "Container": "e83a452b8fb89d78a25a6739457050131ca5c863629a47639530d9ad2008d610",
            "ContainerConfig": {
                "AttachStderr": false,
                "AttachStdin": false,
                "AttachStdout": false,
                "Cmd": [
                    "/bin/sh",
                    "-c",
                    "#(nop) CMD [\"/etc/docker/registry/config.yml\"]"
                ],
                "Domainname": "",
                "Entrypoint": [
                    "/bin/registry"
                ],
                "Env": [
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                ],
                "ExposedPorts": {
                    "5000/tcp": {}
                },
                "Hostname": "e5c68db50333",
                "Image": "c72dce2618dc8f7b794d2b2c2b1e64e0205ead5befc294f8111da23bd6a2c799",
                "Labels": {},
                "OnBuild": [],
                "OpenStdin": false,
                "StdinOnce": false,
                "Tty": false,
                "User": "",
                "Volumes": {
                    "/var/lib/registry": {}
                },
                "WorkingDir": ""
            },
            "Created": "2016-03-08T21:08:15.399680378Z",
            "DockerVersion": "1.9.1",
            "GraphDriver": {
                "Data": null,
                "Name": "aufs"
            },
            "Id": "53773d8552f07b730f3e19979e32499519807d67b344141d965463a950a66e08",
            "Name": "registry:2",
            "Os": "linux",
            "Parent": "f0b1f729f784b755e7bf9c8c2e65d8a0a35a533769c2588f02895f6781ac0805",
            "RepoDigests": [],
            "RepoTags": [
                "registry:2"
            ],
            "Size": 0,
            "VirtualSize": 165808884
        }
    ]
}
'''


class ImageManager(DockerBaseClass):

    def __init__(self, client, results):

        super(ImageManager, self).__init__()

        self.client = client
        self.results = results
        self.name = self.client.module.params.get('name')
        self.log("Gathering facts for images: {0}".format(str(self.name)))
        self.results['results']['images'] = self.get_facts()

    def fail(self, msg):
        self.client.fail(msg)

    def get_facts(self):
        '''
        Lookup and inspect each image name found in the names parameter.

        :returns array of image dictionaries
        '''

        results = []

        names = self.name
        if not isinstance(names, list):
            names = [names]

        for name in names:
            repository, tag = utils.parse_repository_tag(name)
            if not tag:
                tag = 'latest'
            self.log('Fetching image {0}:{1}'.format(repository, tag))
            image = self.client.find_image(name=repository, tag=tag)
            if image:
                results.append(image)

        return results


def main():
    argument_spec = dict(
        name=dict(type='list', required=True),
        log_path=dict(type='str', default='docker_image_facts.log'),
        )

    client = AnsibleDockerClient(
        argument_spec=argument_spec
    )

    results = dict(
        changed=False,
        check_mode=False,
        results=dict()
    )

    ImageManager(client, results)
    client.module.exit_json(**results)


# import module snippets
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()