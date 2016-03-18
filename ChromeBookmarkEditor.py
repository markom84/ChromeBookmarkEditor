#!/usr/bin/python

import json
import os

class ChromeBookmarks(object):

	def __init__(self):
		self.epoch    = "13078095537020784" # Haven't reverse engineered the epoch date_added is calculated from so this is hard coded for now
		self.path     = self.get()
		self.json     = None
		self.ids      = None
		self.titles   = None
		self.children = None
		self.read()

	def get(self):
		"""
		Gets expanded path to Chrome bookmarks json file.

		Returns:
			Expanded path to ~/Library/Application Support/Google/Chrome/Default/Bookmarks

		"""
		path = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Bookmarks')
		if not os.path.isfile(path):
			print "Bookmarks file doesn't appear to exist."
			print "Generating new Bookmarks file."
			self.generate(path)
		return path

	def generate(self, path):
		contents = dict(
			roots=dict(
				bookmark_bar=dict(
					children=list(),
					date_added=self.epoch,
					date_modified="0",
					id="1",
					name="Bookmarks Bar",
					type="folder"
				),
				other=dict(
					children=list(),
					date_added=self.epoch,
					date_modified="0",
					id="2",
					name="Other Bookmarks",
					type="folder"
				),
				synced=dict(
					children=list(),
					date_added=self.epoch,
					date_modified="0",
					id="3",
					name="Mobile Bookmarks",
					type="folder"
				)
			),
			version=1
		)
		with open(path, "w") as outfile:
			json.dump(contents, outfile)

	def read(self):
		with open(self.path, "r") as infile:
			js = json.load(infile)
		self.json     = js
		self.children = self.json['roots']['bookmark_bar']['children']
		self.ids      = [int(bm['id']) for bm in self.children]
		self.titles   = [bm['name'] for bm in self.children]

	def add(self, title, url, index=-1):
		if title in self.titles:
			return
		if index == -1 or index > len(self.children):
			index = len(self.children)
		if not self.ids:
			next_id = 1
		else:
			next_id = max(self.ids) + 1
		new_child = dict(
			date_added=self.epoch,
			id=str(next_id),
			name=title,
			type="url",
			url=url,
		)
		self.children.insert(index, new_child)
		self.ids.append(next_id)
		self.titles.append(title)

	def remove(self, title):
		if title not in self.titles:
			return
		for child in reversed(self.children):
			if child['name'] == title:
				self.ids.remove(int(child['id']))
				self.titles.remove(child['name'])
				self.children.remove(child)

	def move(self, title, index):
		if title not in self.titles:
			return
		if index > len(self.children) or index == -1:
			index = len(self.children)
		elif index < -1:
			index = 0
		for child in self.children:
			if child['name'] == title:
				to_mv = child
				break
		self.children.remove(to_mv)
		self.children.insert(index, to_mv)


	def swap(self, title1, title2):
		if (title1 not in self.titles) or (title2 not in self.titles) or (title1 == title2):
			return
		for index, child in enumerate(self.children):
			if child['name'] == title1:
				index1 = index
				child1 = child
			if child['name'] == title2:
				index2 = index
				child2 = child
		self.children[index1] = child2
		self.children[index2] = child1

	def write(self):
		bak_file = self.path + ".bak"
		if os.path.exists(bak_file):
			os.remove(bak_file)
		self.json.pop("checksum", None)
		with open(self.path, "w") as outfile:
			json.dump(self.json, outfile)




