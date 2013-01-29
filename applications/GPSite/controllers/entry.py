# -*- coding: utf-8 -*-
### required - do no delete

__author__ = 'nulldivide'


def index():
	return  dict()


@auth.requires_login()
def create():
	response.flash = "this is entry create page"

	active_party = db.party(db.party.is_active==True) or redirect(URL('index'))

	entry = db((db.entry.creator==auth.user) & (db.entry.party == active_party)).select().first()

	form = SQLFORM(db.entry, entry)

	if not entry:
		form.vars.party   = active_party
		form.vars.creator =  auth.user
		form.vars.authors = "@"+auth.user['registration_id']

	if form.process().accepted:
		response.flash = 'form accepted'
	elif form.errors:
		response.flash = 'form has errors'
	else:
		response.flash = 'please fill the form'

	return dict(form=form)

