data lake:
- schema on read. 
- dumping data as it is whether its json logs, csvs, videos, images, audio, raw event streams with no table structure.
- decide them later at query time, whatever the data happens to look like when you read it -> elt process hits here.
- pennies per gb.

data warehouse:
- schema on write.
- before data lands here, its already been cleaned, typed and organized into a fixed table structure.
- elt hits here.