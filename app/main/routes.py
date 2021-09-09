from datetime import datetime
from flask import render_template, g, redirect, current_app, request, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProductPriceForm, SearchForm
from app.main import bp
from app.models import Item, Order, Permission, ProductDetailClick, Searches
from app.decorators import permission_required, delivery_required
from app.constants import DELIVERY_FEE


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
    if current_user.is_authenticated:
        current_user.ping()


@bp.route('/order/<int:order_id>')
@login_required
@delivery_required
def order(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash('Pedido não encontrado')
        return redirect(url_for('main.orders'))
    return render_template('main/order.html', title="Pedido " + str(order_id), order=order)


@bp.route('/orders')
@login_required
@delivery_required
def orders():
    return render_template('main/react.html', title="Pedidos", react_app_name='orders', props={})


@login_required
@bp.route('/pedido/<int:order_id>')
def pedido(order_id):
    order = current_user.orders.filter_by(id=order_id).first()
    if not order:
        flash('Pedido não encontrado')
        return redirect(url_for('main.meus_pedidos'))
    return render_template('main/order.html', title="Pedido " + str(order_id), order=order)


@login_required
@bp.route('/meus_pedidos/')
def meus_pedidos():
    page = request.args.get('page', 1, type=int)
    orders = current_user.orders.order_by(
        Order.placed_timestamp.desc()).paginate(page, 5, False)
    next_url = url_for('main.meus_pedidos',
                       page=orders.next_num) if orders.has_next else None
    prev_url = url_for('main.meus_pedidos',
                       page=orders.prev_num) if orders.has_prev else None
    return render_template('main/meus_pedidos.html', title="Pedidos",
                           orders=orders.items, prev_url=prev_url, next_url=next_url)


@login_required
@bp.route('/completed_order')
def completed_order():
    return render_template('main/completed_order.html', title="Sucesso")


@bp.route('/cart')
def cart():
    # response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    # response.headers['Pragma'] = 'no-cache'
    return render_template('main/react.html', title="Carrinho", react_app_name='cart', props={'deliveryFee': DELIVERY_FEE})


@bp.route('/')
def index():
    eans = [
        7896004710891,
        7896023703010,
        891142203014,
        7896422509589,
        7896116860217,
        7896658035388,
        7898569765071,
        7891106914369,
        7896422524452,
        7896422526975,
        7896714211275,
        7891045043588,
        7896015518875,
    ]
    items = Item.get_best_prices(eans)
    return render_template('main/index.html', items=items, search=True)


@bp.route('/search')
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    if not g.search_form.q.data:
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)

    searched_text = g.search_form.q.data.strip()
    Searches.add_search(searched_text)

    items, total = Item.search(
        searched_text, page, current_app.config['ITEMS_PER_PAGE'])

    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['ITEMS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('main/index.html', title='Pesquisa', items=items, next_url=next_url, prev_url=prev_url)


@bp.route('/detail/<int:id>')
def detail(id):
    item = Item.get_ordered_prices_by_id(id)
    if not item:
        flash('Produto não encontrado')
        return redirect(url_for('main.index'))
    ProductDetailClick.click(ean=Item.query.get(id).ean)
    can_edit = False
    if current_user.store_id is not None:
        for i in item:
            if i.store_id == current_user.store_id:
                can_edit = True
    return render_template('main/detail.html', title='Produto', item=item, can_edit=can_edit)


@bp.route('/product/edit/<int:store_id>/<int:ean>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.PRICE)
def product_edit(store_id, ean):
    item = Item.query.filter_by(store_id=store_id, ean=ean).first()
    if not item:
        flash('Produto não encontrado')
        return redirect(url_for('main.index'))

    form = EditProductPriceForm(obj=item)

    if request.method == 'POST' and form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.promotion_price = form.promotion_price.data
        item.promotion_qty = form.promotion_qty.data
        db.session.add(item)
        db.session.commit()
        flash('Produto alterado com sucesso')
        return redirect(url_for('main.detail', ean=item.ean))

    return render_template('main/product_edit.html', title='Editar', item=item, form=form)
