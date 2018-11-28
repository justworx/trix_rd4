#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import * # trix


# WRITER
class Writer(Stream):
	"""Writer of streams."""
	
	# WRITE
	def write(self, data):
		"""Write `data`."""
		try:
			self.write = self.stream.write
			return self.write(data)
		except:
			try:
				self.write = self._writeu
				return self.write(data)
			except:
				self.write = self._writeb
				return self.write(data)
	
	def _writeb(self, data):
		"""Write byte `data`."""
		self.stream.write(data.encode(**self.ek))
	
	def _writeu(self, data):
		"""Write unicode `data`."""
		self.stream.write(data.decode(**self.ek))
	
	# WRITE LINES
	def writelines(self, datalist):
		"""Write a list of lines, `datalist`."""
		try:
			self.writelines = self.stream.writelines
			return self.writelines(datalist)
		except:
			try:
				self.writelines = self._writelinesu
				return self.writelines(datalist)
			except:
				self.writelines = self._writelinesb
				return self.writelines(datalist)
	
	def _writelinesu(self, datalist):
		"""Write a list of lines, `datalist`."""
		for i, v in enumerate(datalist):
			datalist[i] = v.decode(**self.ek)
		return self.stream.writelines(datalist)
	
	def _writelinesb(self, datalist):
		"""Write a list of lines, `datalist`."""
		for i, v in enumerate(datalist):
			datalist[i] = v.encode(**self.ek)
		return self.stream.writelines(datalist)
	
	# FLUSH
	def flush(self):
		"""Flush the contained stream."""
		if self.stream:
			try:
				self.stream.flush()
			except (ValueError, AttributeError):
				# ignore errors where the stream is already closed (or just
				# doesn't have a 'flush' method).
				pass

	# CLOSE
	def close(self):
		"""Close the `self.__stream` stream object."""
		if self.stream:
			self.flush()
			self.stream.close()

