from heatcapacity import fit


class TestFitFirstOrderModel(object):
    def test_from_ck(self):
        c, k = 0.005, 0.002
        model = fit.FirstOrder.from_ck(c, k)
        assert model.heat_capacity == c
        assert model.thermal_conductivity == k
