"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

"""This module contains commands for building Arches."""

from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings
from arches.app.search.base_index import get_index
from arches.app.search.mappings import (
    prepare_terms_index,
    prepare_concepts_index,
    delete_terms_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
    prepare_resource_relations_index,
    delete_resource_relations_index,
)
import arches.app.utils.index_database as index_database


class Command(BaseCommand):
    """
    Commands for running common elasticsearch commands

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            choices=[
                "install",
                "setup_indexes",
                "delete_indexes",
                "index_database",
                "index_concepts",
                "index_resources",
                "index_resource_relations",
                "add_index",
                "delete_index",
            ],
            help="Operation Type; "
            + "'setup_indexes'=Creates the indexes in Elastic Search needed by the system"
            + "'delete_indexes'=Deletes all indexs in Elasticsearch required by the system"
            + "'index_database'=Indexes all the data (resources, concepts, and resource relations) found in the database"
            + "'index_concepts'=Indxes all concepts from the database"
            + "'index_resources'=Indexes all resources from the database"
            + "'index_resource_relations'=Indexes all resource to resource relation records"
            + "'add_index'=Register a new index in Elasticsearch"
            + "'delete_index'=Deletes a named index from Elasticsearch",
        )

        parser.add_argument(
            "-d", "--dest_dir", action="store", dest="dest_dir", default="", help="Directory from where you want to run elasticsearch."
        )

        parser.add_argument(
            "-p", "--port", action="store", dest="port", default=settings.ELASTICSEARCH_HTTP_PORT, help="Port to use for elasticsearch."
        )

        parser.add_argument(
            "-b",
            "--batch_size",
            action="store",
            dest="batch_size",
            type=int,
            default=settings.BULK_IMPORT_BATCH_SIZE,
            help="The number of records to index as a group, the larger the number to more memory required",
        )

        parser.add_argument(
            "-c",
            "--clear_index",
            action="store",
            dest="clear_index",
            default=True,
            help="Set to True(default) to remove all the resources from the index before the reindexing operation",
        )

        parser.add_argument("-n", "--name ", action="store", dest="name", default=None, help="Name of the custom index")

    def handle(self, *args, **options):
        if options["operation"] == "setup_indexes":
            self.setup_indexes()

        if options["operation"] == "add_index":
            self.register_index(name=options["name"])

        if options["operation"] == "delete_indexes":
            self.delete_indexes()

        if options["operation"] == "delete_index":
            self.remove_index(name=options["name"])

        if options["operation"] == "index_database":
            if options["name"] is not None:
                index_database.index_resources(
                    clear_index=options["clear_index"], index_name=options["name"], batch_size=options["batch_size"]
                )
            else:
                index_database.index_db(clear_index=options["clear_index"], batch_size=options["batch_size"])

        if options["operation"] == "index_concepts":
            index_database.index_concepts(clear_index=options["clear_index"], batch_size=options["batch_size"])

        if options["operation"] == "index_resources":
            index_database.index_resources(clear_index=options["clear_index"], batch_size=options["batch_size"])

        if options["operation"] == "index_resource_relations":
            index_database.index_resource_relations(clear_index=options["clear_index"], batch_size=options["batch_size"])

    def register_index(self, name):
        es_index = get_index(name)
        es_index.prepare_index()

    def remove_index(self, name):
        es_index = get_index(name)
        es_index.delete_index()

    def setup_indexes(self):
        prepare_terms_index(create=True)
        prepare_concepts_index(create=True)
        prepare_resource_relations_index(create=True)
        prepare_search_index(create=True)

        # add custom indexes
        for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
            self.register_index(index["name"])

    def delete_indexes(self):
        delete_terms_index()
        delete_concepts_index()
        delete_search_index()
        delete_resource_relations_index()

        # remove custom indexes
        for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
            self.remove_index(index["name"])
