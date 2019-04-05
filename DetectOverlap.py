from arcpy import da, GetParameterAsText, AddMessage, SelectLayerByAttribute_management
import pandas as pd

EventTable = GetParameterAsText(0)
RouteId = GetParameterAsText(1)
FromMeas = GetParameterAsText(2)
ToMeas = GetParameterAsText(3)
OverlapOID = GetParameterAsText(4)

OID_field = 'OID@'
np_array = da.FeatureClassToNumPyArray(EventTable, [RouteId, FromMeas, ToMeas, OID_field])
df = pd.DataFrame(np_array)
AddMessage(list(df))
route_list = df[RouteId].unique().tolist()

for route in route_list:
    df_route = df.loc[df[RouteId] == route]

    flipped_i = df_route.loc[df_route[FromMeas] > df_route[ToMeas]].index
    df_route.loc[flipped_i, [FromMeas, ToMeas]] = df_route.loc[flipped_i, [ToMeas, FromMeas]].values
    df_route.sort_values(by=[FromMeas, ToMeas], inplace=True)

    for index, row in df_route.iterrows():
        complete_overlap = ((df_route[FromMeas] > row[FromMeas]) & (df_route[ToMeas] < row[ToMeas]))
        partial_front_overlap = ((df_route[FromMeas] < row[FromMeas]) & (df_route[ToMeas] > row[FromMeas]))
        overlap_i = df_route.loc[partial_front_overlap | complete_overlap].index
        if len(overlap_i) != 0:
            OID_list = df_route.loc[overlap_i, OID_field].values.tolist()
            OID_list = str(OID_list).strip('[]')

            if len(OID_list) > 195:
                OID_list = None
        else:
            OID_list = None

            with da.UpdateCursor(EventTable, OverlapOID,
                                 where_clause="OBJECTID IN ({0})".format(row[OID_field])) as cursor:
                for update_row in cursor:
                    update_row[0] = OID_list
                    cursor.updateRow(update_row)
