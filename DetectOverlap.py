from arcpy import da, GetParameterAsText, AddMessage
import pandas as pd
import numpy as np

EventTable = GetParameterAsText(0)
RouteId = GetParameterAsText(1)
FromMeas = GetParameterAsText(2)
ToMeas = GetParameterAsText(3)
OutputTable = GetParameterAsText(4)
Resolution = 0.01

np_array = da.FeatureClassToNumPyArray(EventTable, [RouteId, FromMeas, ToMeas, 'SHAPE@M'])
df = pd.DataFrame(np_array)
route_list = df[RouteId].unique().tolist()

for route in route_list:
    df_route = df.loc[df[RouteId] == route]
    df_route.sort_values(by=[FromMeas, ToMeas], inplace=True)
    df_route.reset_index(drop=True, inplace=True)

    for index, row in df_route.iterrows():
        if index == 0:
            from_m = row[FromMeas]
            to_m = row[ToMeas]
        else:
            pass