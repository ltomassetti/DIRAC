########################################################################
# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/WorkloadManagementSystem/Agent/TaskQueueAgent.py,v 1.24 2009/01/28 12:03:02 acasajus Exp $
# File :   TaskQueueAgent.py
# Author : Stuart Paterson
########################################################################

"""  The Task Queue Agent acts after Job Scheduling to place the ready jobs
     into a Task Queue.
"""

__RCSID__ = "$Id: TaskQueueAgent.py,v 1.24 2009/01/28 12:03:02 acasajus Exp $"

from DIRAC.WorkloadManagementSystem.Agent.OptimizerModule  import OptimizerModule
from DIRAC.WorkloadManagementSystem.DB.TaskQueueDB         import TaskQueueDB
from DIRAC.ConfigurationSystem.Client.Config               import gConfig
from DIRAC.Core.Utilities.ClassAd.ClassAdLight             import ClassAd
from DIRAC.Core.Security.CS                                import getPropertiesForGroup
from DIRAC                                                 import S_OK, S_ERROR, Time
import string,re

class TaskQueueAgent(OptimizerModule):

  #############################################################################
  def initializeOptimizer(self):
    """Initialize specific parameters for TaskQueueAgent.
    """
    self.waitingStatus      = self.am_getOption( 'WaitingStatus', 'Waiting' )
    self.waitingMinorStatus = self.am_getOption( 'WaitingMinorStatus', 'Pilot Agent Submission' )
    try:
      self.taskQueueDB        = TaskQueueDB()
    except Exception, e:
      return S_ERROR( "Cannot initialize taskqueueDB: %s" % str(e) )
    return S_OK()

  #############################################################################
  def checkJob( self, job, classAdJob ):
    """This method controls the checking of the job.
    """
    result = self.insertJobInQueue( job, classAdJob )
    if not result['OK']:
      self.log.warn(result['Message'])
      return S_ERROR( result[ 'Message' ] )

    result = self.updateJobStatus( job, self.waitingStatus, self.waitingMinorStatus )
    if not result['OK']:
      self.log.warn(result['Message'])

    return S_OK()

  #############################################################################
  def insertJobInQueue( self, job, classAdJob ):
    """ Check individual job and add to the Task Queue eventually.
    """
    #
    requirements = classAdJob.get_expression("Requirements")
    jobType = classAdJob.get_expression("JobType").replace('"','')
    submitPool = classAdJob.get_expression( "SubmitPool" ).replace('"','')
    ownerDN = classAdJob.get_expression( "OwnerDN" ).replace('"','')
    ownerGroup = classAdJob.get_expression( "OwnerGroup" ).replace('"','')

    jobReq = classAdJob.get_expression("JobRequirements")
    classAdJobReq = ClassAd(jobReq)
    jobReqDict = {}
    for name in self.taskQueueDB.getSingleValueTQDefFields():
      if classAdJobReq.lookupAttribute(name):
        if name == 'CPUTime':
          jobReqDict[name] = classAdJobReq.getAttributeInt(name)
        else:
          jobReqDict[name] = classAdJobReq.getAttributeString(name)

    for name in self.taskQueueDB.getMultiValueTQDefFields():
      if classAdJobReq.lookupAttribute(name):
        jobReqDict[name] = classAdJobReq.getListFromExpression(name)

    jobPriority = classAdJobReq.getAttributeInt( 'UserPriority' )

    result = self.taskQueueDB.insertJob( job, jobReqDict, jobPriority )
    if not result[ 'OK' ]:
      self.log.error( "Cannot insert job %s in task queue: %s" % ( job, result[ 'Message' ] ) )
      return S_ERROR( "Cannot insert in task queue" )
    return S_OK()

  #EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#
