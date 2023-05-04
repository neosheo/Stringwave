from flask import render_template, request, redirect
from cogmera import *
from webapp import *


@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        genres = request.form.getlist('genres')
        genres = ';'.join(genres)
        styles = request.form.getlist('styles')
        styles = ';'.join(styles)
        decade = request.form['decades']
        year = request.form['years']
        country = request.form['countries']
        sort_method = request.form['sort_methods']
        sort_order = request.form['order']
        albums_to_find = request.form['number']
        new_config = Config(genres=genres, styles=styles, decade=decade, year=year, country=country, sort_method=sort_method, sort_order=sort_order, albums_to_find=albums_to_find)
        db.session.add(new_config)
        db.session.commit()
    return render_template('config.html', genres=Genres.query.order_by(Genres.genre_id).all(), styles=Styles.query.order_by(Styles.style_id).all(), decades=Decades.query.order_by(Decades.decade_id).all(), countries=Countries.query.order_by(Countries.country_id).all(), years=Years.query.order_by(Years.year_id).all(), sort_methods=SortMethods.query.order_by(SortMethods.sort_method_id).all())


@app.route('/dump_config', methods=['GET'])
def dump():
	configs = Config.query.order_by(Config.config_id).all()
	return render_template('dump_config.html', configs=configs) 


@app.route('/delete_config', methods=['POST'])
def delete():
	db.session.query(Config).filter_by(config_id=request.form['delete_config']).delete()
	db.session.commit()
	return redirect('/dump_config')	

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
