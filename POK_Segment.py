from arcpy import da, Point, PointGeometry, GetParameterAsText, Describe, CreateFeatureclass_management, env, \
    AddField_management, GetParameter, SetParameter, AddMessage

POK_Table = GetParameterAsText(0)
X_Start = GetParameterAsText(1)
Y_Start = GetParameterAsText(2)
X_End = GetParameterAsText(3)
Y_End = GetParameterAsText(4)
POK_RID = GetParameterAsText(5)
SearchRadius = GetParameterAsText(6)
OutputLine = GetParameterAsText(7)
IncludeAll = GetParameter(8)

Network = 'ELRS.National_Network2018'
NetworkRID = 'ROUTEID'
SDE_Connection = 'E:\SMD_Script\ELRS@GEODBBM 144.sde'
env.workspace = SDE_Connection

out_rid = ['ROUTEID', 'TEXT']
out_from = ['FROM_M', 'DOUBLE']
out_to = ['TO_M', 'DOUBLE']
out_dist_st = ['STA_DIST', 'DOUBLE']
out_dist_end = ['END_DIST', 'DOUBLE']
field_definition = [out_rid, out_from, out_to, out_dist_end, out_dist_st]

field_names = [field[0] for field in field_definition]
field_names_shapes = field_names
field_names_shapes.append('SHAPE@')
Network_SpatRef = Describe(Network).spatialReference

# Create an empty feature class for storing all the line segment
CreateFeatureclass_management(env.scratchGDB, OutputLine, geometry_type='POLYLINE', spatial_reference=Network_SpatRef)
env.overwriteOutput = True # Allow overwrite the output

for field in field_definition:
    field_name = field[0]  # Field name
    field_type = field[1]  # Field type
    # Create all the necessary field for the line feature class
    AddField_management(env.scratchGDB+'/'+OutputLine, field_name, field_type)

# The insert cursor for line feature class
line_ins = da.InsertCursor(env.scratchGDB+'/'+OutputLine, field_names_shapes)

with da.SearchCursor(POK_Table, [X_Start, Y_Start, X_End, Y_End, POK_RID]) as search:
    for t_row in search:  # Iterate over all available POK segment
        route = t_row[4]  # The POK route ID

        # Start Point and End Point in WGS 1984 projection system
        start_point = PointGeometry(Point(t_row[0], t_row[1])).projectAs('4326')
        end_point = PointGeometry(Point(t_row[2], t_row[3])).projectAs('4326')

        # Start Point and End Point in same projection as the Network Feature Class
        start_point = start_point.projectAs(Network_SpatRef)
        end_point = end_point.projectAs(Network_SpatRef)

        route_found = False  # Variable for determining if the requested routes exist in the Network FC

        # Iterate over all available row in Network Feature Class
        with da.SearchCursor(Network, 'SHAPE@', where_clause="{0}='{1}'".format(NetworkRID, route)) as search_cur:
            for s_row in search_cur:
                route_found = True  # If the route exist
                route_geom = s_row[0]  # The route geometry object
                from_m = route_geom.measureOnLine(start_point)  # Divided by 1000 to converts the unit to KM
                to_m = route_geom.measureOnLine(end_point)

                dist_from = route_geom.distanceTo(start_point)  # The distance of Start and End point to a Route
                dist_to = route_geom.distanceTo(end_point)

        if route_found:

            if IncludeAll:
                segment_geom = route_geom.segmentAlongLine(from_m, to_m)
                line_ins.insertRow([route, from_m, to_m, dist_to, dist_from, segment_geom])

            elif not IncludeAll:
                if (dist_from < SearchRadius) and (dist_to < SearchRadius):
                    segment_geom = route_geom.segmentAlongLine(from_m, to_m)
                    line_ins.insertRow([route, from_m, to_m, dist_to, dist_from, segment_geom])

SetParameter(9, env.scratchGDB+'/'+OutputLine)
