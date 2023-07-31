
#
# This is an example of how you can access the SqLite DBs when you are using the DBSpy
# with a support bundle.
#
# Access to the DB is via the self.parent.dbConnector attribute

print self.parent.dbConnector.executeAll("select * from netapp_model.aggregate")