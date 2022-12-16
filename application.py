from flask import Flask, render_template, request, url_for

application = Flask(__name__)


@application.route('/')
def home():
    return render_template("home.html")


@application.route('/calc_risk')
def risk_calc():
    return render_template("calc_risk.html")


@application.route('/calc_result', methods=["POST", "GET"])
def calc_result():
    """
    This function calculates different characteristics of financial trades.
    f.E Stop-Loss, Take-Profit, risk-reward ratio, position-size
    """
    # ------------------------Stückzahl einlesen default Wert = 1---------------------#
    #
    quantity = request.args.get("quantity")
    if quantity:
        quantity = int(quantity)
    else:
        quantity = 1
    # --------------------------------------------------------------------------------#
    # Kurs einlesen, wenn nicht vorhanden --> user_message
    kurs_str = request.args.get("kurs")
    if not kurs_str:
        # No price input case
        return render_template("calc_result.html", user_warning="Bitte Kurs eingeben")
    else:
        kurs_int = int(kurs_str)
    # --------------------------------------------------------------------------------#
    total_invest = kurs_int * quantity
    # -------------------------------Loss Fälle einlesen-------------------------------#
    selling_threshold_loss_dollar_str = request.args.get("selling_threshold_loss_dollar")
    loss_prct_str = request.args.get("loss_prct")
    # -------------------------------Win Fälle einlesen-------------------------------#
    selling_threshold_win_dollar_str = request.args.get("selling_threshold_win_dollar")
    win_prct_str = request.args.get("win_prct")
    # --------------------------------Tolerierten Verlust einlesen--------------------------- #
    tolerated_loss_str = request.args.get("tolerated_loss")

    crv_str = request.args.get("crv")

    # --------------------------------Abkürzungen--------------------------------------#
    s_t_l_d_s = selling_threshold_loss_dollar_str
    s_t_w_d_s = selling_threshold_win_dollar_str
    rt = render_template
    # -------------------------All variables which can be None set to None-------------- #
    s_t_l_d_i = s_t_w_d_i = loss_per_stock = total_loss \
        = loss_prct_int = win_prct_int = \
        win_per_stock = total_win = crv_float = tolerated_loss_int = None

    # ------------------------ Fall beide Loss Felder gefüllt----------------------------#
    if s_t_l_d_s and loss_prct_str:
        return rt("calc_result.html", user_warning="Bitte nur eine Größe eingeben.")
    # ------------------------ Fall beide Win Felder gefüllt----------------------------#
    if s_t_w_d_s and win_prct_str:
        return rt("calc_result.html", user_warning="Bitte nur eine Größe eingeben")

    # nur Stop-Loss $
    if s_t_l_d_s:
        s_t_l_d_i = int(s_t_l_d_s)
        loss_prct_int = round((kurs_int - s_t_l_d_i) / kurs_int * 100)

    # nur Stop-Loss %
    if loss_prct_str:
        loss_prct_int = int(loss_prct_str)
        s_t_l_d_i = kurs_int * ((100 - loss_prct_int) / 100)

    # -------------------------Fall tolerated_loss no s_t_l_d_i-------------------------------------- #
    if tolerated_loss_str and not s_t_l_d_i:
        return rt("calc_result.html", user_warning=" Bitte ein Verlust eintragen")

    if tolerated_loss_str:
        tolerated_loss_int = int(tolerated_loss_str)
        quantity = tolerated_loss_int / (kurs_int - s_t_l_d_i)

    # nur Take-Profit $
    if s_t_w_d_s:
        s_t_w_d_i = int(s_t_w_d_s)
        win_prct_int = round((s_t_w_d_i - kurs_int) / kurs_int * 100)

    # nur Take-Profit %
    if win_prct_str:
        win_prct_int = int(win_prct_str)
        s_t_w_d_i = round(kurs_int * ((100 + win_prct_int) / 100))

    # Loss Angabe größer als Kurs
    if s_t_l_d_i and s_t_l_d_i > kurs_int:
        return rt("calc_result.html", user_warning="Die Verlust Angabe muss kleiner sein als der Kurs")

    # Win Angabe kleiner als Kurs
    if s_t_w_d_i and s_t_w_d_i < kurs_int:
        return rt("calc_result.html", user_warning="Die Gewinn Angabe muss größer sein als der Kurs")

    if not s_t_l_d_i and not s_t_w_d_i:
        return render_template("calc_result.html", user_warning="Mehr Angaben benötigt.")

    if s_t_l_d_i:
        loss_per_stock = kurs_int - s_t_l_d_i
        total_loss = quantity * loss_per_stock

    if s_t_w_d_i:
        win_per_stock = s_t_w_d_i - kurs_int
        total_win = quantity * win_per_stock

    if crv_str:
        crv_float = float(crv_str)

    if s_t_l_d_i and s_t_w_d_i and crv_float:
        return rt("calc_result.html", user_warning="Zu viele Angaben.")

    if s_t_l_d_i and s_t_w_d_i:
        crv_float = round(win_per_stock / loss_per_stock, 1)

    # CRV and Loss
    if s_t_l_d_i and crv_float and not s_t_w_d_i:
        win_per_stock = round((kurs_int - s_t_l_d_i) * crv_float)
        s_t_w_d_i = kurs_int + win_per_stock
        win_prct_int = round(100 * win_per_stock / kurs_int)
        total_win = quantity * win_per_stock

    # CRV and Win
    if s_t_w_d_i and crv_float and not s_t_l_d_i:
        loss_per_stock = round((s_t_w_d_i - kurs_int) / crv_float)
        s_t_l_d_i = kurs_int - loss_per_stock
        loss_prct_int = round(loss_per_stock / kurs_int * 100)
        total_loss = quantity * loss_per_stock

    return rt("calc_result.html", kurs=kurs_int, total_invest=total_invest,
              s_t_l_d=s_t_l_d_i, total_loss=total_loss, loss_prct=loss_prct_int, loss_per_stock=loss_per_stock,
              s_t_w_d=s_t_w_d_i, total_win=total_win, win_prct=win_prct_int, win_per_stock=win_per_stock,
              crv=crv_float, quantity=quantity, tolerated_loss=tolerated_loss_int)


if __name__ == '__main__':
    application.run()
