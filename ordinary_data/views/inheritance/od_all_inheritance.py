#!/usr/bin/env python

import imp
import os
import sys

pgiv = imp.load_source('PGInheritanceView', os.path.join(os.path.dirname(__file__), '../../../metaproject/postgresql/pg_inheritance_view/pg_inheritance_view.py'))

if len(sys.argv) > 1:
	pg_service = sys.argv[1]
else:
	pg_service = 'qwat_test'


qwat_node_element = """
table: qwat_od.node
alias: node
pkey: id
pkey_value: qwat_od.fn_node_create(NEW.geometry)
pkey_value_create_entry: true
schema: qwat_od
generate_child_views: True

custom_delete: "PERFORM qwat_od.fn_node_set_type(OLD.id)"

trigger_pre: >
  \t\t-- altitude is prioritary on Z value of the geometry (if both changed, only altitude is taken into account)
  \t\tIF NEW.altitude IS NULL THEN
  \t\t	NEW.altitude := NULLIF( ST_Z(NEW.geometry), 0.0); -- 0 is the NULL value
  \t\tEND IF;
  \t\t-- TODO handle going to NULL on update
  \t\tIF	NEW.altitude IS NULL     AND ST_Z(NEW.geometry) <> 0.0 OR
  \t\t		NEW.altitude IS NOT NULL AND ( ST_Z(NEW.geometry) IS NULL OR ST_Z(NEW.geometry) <> NEW.altitude ) THEN
  \t\t\t\tNEW.geometry := ST_SetSRID( ST_MakePoint( ST_X(NEW.geometry), ST_Y(NEW.geometry), COALESCE(NEW.altitude,0) ), ST_SRID(NEW.geometry) );
  \t\tEND IF;


children:
  element:
    table: qwat_od.network_element
    pkey: id
    alter:
      orientation:
        read: COALESCE(element.orientation, -node._pipe_orientation)
    alias: element
    table: qwat_od.vw_node_element
    pkey: id
    pkey_value: NEW.id
    schema: qwat_od
    generate_child_views: True

    children:
        installation:
            table: qwat_od.vw_qwat_installation
            pkey: id
            alias: installation
            table: qwat_od.installation
            pkey: id
            pkey_value: NEW.id
            generate_child_views: False
            allow_type_change: false

            schema: qwat_od

            children:
                chamber:
                    table: qwat_od.chamber
                    pkey: id

                pressurecontrol:
                    table: qwat_od.pressurecontrol
                    pkey: id

                pump:
                    table: qwat_od.pump
                    pkey: id

                source:
                    table: qwat_od.source
                    pkey: id

                tank:
                    table: qwat_od.tank
                    pkey: id

                treatment:
                    table: qwat_od.treatment
                    pkey: id

            merge_view:
                name: vw_qwat_installation
                allow_type_change: false

        hydrant:
            table: qwat_od.hydrant
            pkey: id

        part:
            table: qwat_od.part
            pkey: id
            alter:
                fk_pipe:
                    write: qwat_od.fn_pipe_get_id(NEW.geometry)

        meter:
            table: qwat_od.meter
            pkey: id

        subscriber:
            table: qwat_od.subscriber
            pkey: id

        samplingpoint:
            table: qwat_od.samplingpoint
            pkey: id

    merge_view:
        name: vw_qwat_network_element
        allow_type_change: false
        allow_parent_only: true
        merge_columns:
            parcel:
                meter: parcel
                subscriber: parcel
                installation: parcel
            networkseparation:
                installation: networkseparation
            fk_pipe:
                meter: fk_pipe
                part: fk_pipe
                subscriber: fk_pipe


merge_view:
  name: vw_qwat_node
  allow_type_change: false
  allow_parent_only: true
"""

print pgiv.PGInheritanceView(pg_service, qwat_node_element).sql_all()
