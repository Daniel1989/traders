from models import Ip


def get_high_score_ip():
    try:
        return Ip.select(Ip, Ip.ip, Ip.success_num).where(Ip.status == 'success').order_by(Ip.success_num.desc()).get()
    except Exception as e:
        return None
