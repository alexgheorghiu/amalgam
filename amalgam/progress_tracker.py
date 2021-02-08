class ProgressTracker:

	def __init__(self):
		self.progresses = {}

	@staticmethod
	def _msg_to_progress(msg):
		progress = {}
		progress['visited'] = msg["visited"]
		progress['to_visit'] = msg["to_visit"]
		progress['max_links'] = msg["max_links"]
		progress['status'] = msg["status"]
		progress['crawlId'] = msg["crawlId"]

		return progress

	def set_progress(self, crawlId, msg):
		progress = self._msg_to_progress(msg)
		self.progresses[str(crawlId)] = progress
		

	def get_progress(self,crawlId):
		if not crawlId in self.progresses.keys():
			self.progresses[str(crawlId)] = {
				"visited" : 0,
				"to_visit" : 0,
				"max_links" : 0,
				"status": ""
			}
		return self.progresses[crawlId]