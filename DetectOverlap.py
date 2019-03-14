from arcpy import da, GetParameterAsText
import pandas as pd

EventTable = GetParameterAsText(0)
RouteId = GetParameterAsText(1)
FromMeas = GetParameterAsText(2)
ToMeas = GetParameterAsText(3)
OutputTable = GetParameterAsText(4)

np_array = da.FeatureClassToNumPyArray(EventTable, [RouteId, FromMeas, ToMeas, 'SHAPE@M'])
df = pd.DataFrame(np_array)
