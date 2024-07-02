from models import Ip


def get_high_score_ip():
    try:
        return Ip.select(Ip, Ip.ip, Ip.success_num).where(Ip.status == 'success', Ip.success_num < 5).order_by(Ip.success_num.desc()).get()
    except Exception as e:
        return None

def get_useable_ip():
    try:
        return Ip.select(Ip.ip).where(Ip.status == 'success', Ip.success_num == 5, Ip.cost_time < 1000).limit(100)
    except Exception as e:
        return None
