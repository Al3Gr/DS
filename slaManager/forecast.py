import itertools
import math
import statsmodels.api as sm

class forecast:

    best_params_metrica = {}

    def __init__(self, nomeMetrica, df):
        if nomeMetrica in self.best_params_metrica:
            order = self.best_params_metrica[nomeMetrica][:3]
            seasonal_order = self.best_params_metrica[nomeMetrica][3:]

            model = sm.tsa.SARIMAX(df,
                                    order=order,
                                    seasonal_order=seasonal_order)
            result = model.fit(disp=False)
            self.best_result = result
            
            return

        p_values = range(0, 3)  # Autoregressive order
        d_values = [0]          # Differencing order
        q_values = range(0, 3)  # Moving average order
        P_values = range(0, 3)  # Seasonal autoregressive order
        D_values = range(0, 3)  # Seasonal differencing order
        Q_values = range(0, 3)  # Seasonal moving average order
        m_values = [1440]         # Seasonal period (dovrebbe essere 24h=60*24=1440)

        param_combinations = list(itertools.product(p_values,
                                            d_values,
                                            q_values,
                                            P_values,
                                            D_values,
                                            Q_values,
                                            m_values))

        self.best_result = None
        best_aic = float("inf")
        best_params = None

        for params in param_combinations:
            order = params[:3]
            seasonal_order = params[3:]

            try:
                model = sm.tsa.SARIMAX(df,
                                    order=order,
                                    seasonal_order=seasonal_order)
                result = model.fit(disp=False)
                aic = result.aic

                # Ensure the convergence of the model
                if not math.isinf(result.zvalues.mean()):
                    if aic < best_aic:
                        best_aic = aic
                        best_params = params
                        self.best_result = result
                        
            except:
                continue

        self.best_params_metrica[nomeMetrica] = best_params

    def get_ConfInt(self, nsteps):
        if self.best_result is None:
            raise Exception("Errore nella chiamata del metodo")

        forecast = self.best_resultresult.get_forecast(steps=nsteps)
        return forecast.conf_int()

        