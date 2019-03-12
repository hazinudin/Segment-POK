from arcpy import da, Point, PointGeometry, GetParameterAsText, Describe

Network = GetParameterAsText(0)
POK_Table = GetParameterAsText(1)
X_Start = GetParameterAsText(2)
Y_Start = GetParameterAsText(3)
X_End = GetParameterAsText(4)
Y_End = GetParameterAsText(5)
POK_RouteID = GetParameterAsText(6)
Network_RouteID = GetParameterAsText(7)
POK_FromM = GetParameterAsText(8)
POK_ToM = GetParameterAsText(9)
SearchRadius = GetParameterAsText(10)
DistanceStart = GetParameterAsText(11)
DistanceEnd = GetParameterAsText(12)

Network_SpatRef = Describe(Network).spatialReference

with da.UpdateCursor(POK_Table,
                     [X_Start, Y_Start, X_End, Y_End, POK_FromM, POK_ToM, POK_RouteID, DistanceStart, DistanceEnd]) \
        as update_cur:
    for t_row in update_cur:
        start_point = PointGeometry(Point(t_row[0], t_row[1])).projectAs('4326')
        end_point = PointGeometry(Point(t_row[2], t_row[3])).projectAs('4326')

        start_point = start_point.projectAs(Network_SpatRef)
        end_point = end_point.projectAs(Network_SpatRef)

        with da.SearchCursor(Network, 'SHAPE@', where_clause="{0}='{1}'".format(Network_RouteID, t_row[6])) as search_cur:
            for s_row in search_cur:
                from_m = s_row[0].measureOnLine(start_point)/1000  # Divided by 1000 to converts the unit to KM
                to_m = s_row[0].measureOnLine(end_point)/1000

                dist_from = s_row[0].distanceTo(start_point)
                dist_to = s_row[0].distanceTo(end_point)

        t_row[4] = from_m
        t_row[5] = to_m
        t_row[7] = dist_from
        t_row[8] = dist_to
        update_cur.updateRow(t_row)