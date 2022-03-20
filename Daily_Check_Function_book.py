import pandas as pd
import numpy as np
from datetime import datetime as dt
import PySimpleGUI as sg
import xlwings as xw
import glob


def check_ticker(df, report_date):
    vitruvius_summary_sheet_loc = "G:/network users/SICAV/Monthly Letters/Structure Report Project/Vitruvius Summary Sheet.xlsx"

    # set up file location for MS swaps spreadsheet, in the future, if other sub-accounts initiated new swaps, we can also get from here
    ms_swap_vgc_loc = (
        "G:/network users/SICAV/Managers/Greenwoods/SWAPS/"
        + dt.today().strftime("%Y")
        + "/"
        + report_date
        + "-VGCEQ-GW-Excel.csv"
    )
    ms_swap_vgc_loc_pre_yr = (
        "G:/network users/SICAV/Managers/Greenwoods/SWAPS/"
        + str(dt.today().year - 1)
        + "/"
        + report_date
        + "-VGCEQ-GW-Excel.csv"
    )

    ms_swap_vae_loc = (
        "G:/network users/SICAV/Managers/Indus/SWAP/"
        + dt.today().strftime("%Y")
        + "/"
        + report_date
        + "-VGCEQ-GW-Excel.csv"
    )
    ms_swap_vae_loc_pre_yr = (
        "G:/network users/SICAV/Managers/Indus/SWAP/"
        + str(dt.today().year - 1)
        + "/"
        + report_date
        + "-VGCEQ-GW-Excel.csv"
    )

    ms_swap_lookup = {
        "VITRUVIUS GREATER CHINA EQUITY - GW SUB-ACCOUNT": [
            ms_swap_vgc_loc,
            ms_swap_vgc_loc_pre_yr,
        ],
        "VITRUVIUS ASIAN EQUITY PORTFOLIO": [ms_swap_vae_loc, ms_swap_vae_loc_pre_yr],
    }

    suc_acc_name = df["Sub-Fund_long_name"].unique()[0]

    cond_1 = df["Instr_Category"] == "VMOB"
    cond_1_2 = df["Instr_long_name"].str.contains("P-Note", regex=False)
    cond_2 = df["Instr_Category"] == "SWAT"
    cond_2_1 = df["Stock_Type"] == "HOBI"
    cond_2_2 = df["Long_short"] == "RECU"
    cond_3 = df["Bloomberg Code"].isnull()
    col_to_keep = [
        "Sub-Fund_long_name",
        "Instr_Category",
        "Instr_long_name",
        "Bloomberg Code",
    ]

    missing_tks = df.loc[
        (cond_3 & (cond_2 & cond_2_1 & cond_2_2)) | (cond_1 & cond_1_2), col_to_keep
    ].copy()
    missing_tks.set_index("Instr_long_name", drop=False, inplace=True)
    if len(missing_tks) == 0:
        pass
    else:
        # import the summary control sheet

        deri_map = pd.read_excel(
            vitruvius_summary_sheet_loc, sheet_name="OTC_Derivatives"
        )
        deri_map.set_index("Instr_long_name", inplace=True)
        missing_tks = missing_tks.join(
            deri_map[["name_show_on_MS", "Bloomberg Code"]], how="left", rsuffix="_map"
        )
        # using GUI to alter user that a new swap was initiated in the FFPOS file, and the name and bloomberg code of the
        # new swap needs to be manually added to the table

        missing_ticker_df = pd.DataFrame(
            columns=[
                "Sub-Fund_long_name",
                "Instr_Category",
                "Instr_long_name",
                "Bloomberg Code",
                "name_show_on_MS",
            ]
        )

        if len(missing_tks[missing_tks["Bloomberg Code_map"].isnull()]) == 0:
            print("No new swap or p-notes being initiated...")
        else:
            for index, row in missing_tks[
                missing_tks["Bloomberg Code_map"].isnull()
            ].iterrows():
                sub_fund = row[0]
                instr_cat = row[1]
                instr_name = index

                layout = [
                    [
                        sg.Text(
                            "A new swap/p-notes was initiated by the manager, please manually input the name and ticker",
                            font=(25),
                        )
                    ],
                    [sg.Text(f"The portfolio name is {sub_fund}", size=(70, 2))],
                    [
                        sg.Text(
                            f"The new instrument name from FFPOS file is {instr_name}",
                            size=(70, 2),
                        )
                    ],
                    #                     [sg.Text('Input swap name from Morgan Stanley Swap file, or leave blank for p-notes: ',size=(70,2)), sg.InputText(),sg.FileBrowse(key="-FILEBROWSE-")],
                    [
                        sg.Text(
                            "Input swap name from Morgan Stanley Swap file, or leave blank for p-notes: ",
                            size=(70, 2),
                        ),
                        sg.InputText(),
                    ],
                    [
                        sg.Text(
                            "Input BBG Ticker in '001234 CH Equity' format (case sensitive): ",
                            size=(70, 2),
                        ),
                        sg.InputText(),
                    ],
                    [sg.OK(), sg.Cancel()],
                ]
                window = sg.Window("Input New Swap/P-Notes Information").Layout(layout)
                #         window['-FILEBROWSE-'].InitialFolder = 'G:/network users/SICAV/Managers'
                button, ticker = window.Read()
                ms_name = ticker[0]
                bbg_ticker = ticker[1]

                window.Close()

                input_series = pd.DataFrame(
                    [[sub_fund, instr_cat, instr_name, bbg_ticker, ms_name]],
                    columns=[
                        "Sub-Fund_long_name",
                        "Instr_Category",
                        "Instr_long_name",
                        "Bloomberg Code",
                        "name_show_on_MS",
                    ],
                )

                missing_ticker_df = pd.concat([missing_ticker_df, input_series])

            missing_ticker_df.set_index("Instr_long_name", inplace=True)
            deri_map = pd.concat([deri_map, missing_ticker_df])
            deri_map.sort_values(
                by=["Sub-Fund_long_name", "Instr_Category"], inplace=True
            )
            # Create xlwings application
            app = xw.App()
            # Open and load Structure Report Template
            wb = xw.Book(vitruvius_summary_sheet_loc)
            sheet = wb.sheets["OTC_Derivatives"]
            sheet.clear_contents()
            sheet.range("A1").options(index=True).value = deri_map
            wb.save(vitruvius_summary_sheet_loc)
            wb.close()
            # Quit xlwings application
            app.quit()

        missing_ticker_df["Bloomberg Code_map"] = missing_ticker_df["Bloomberg Code"]
        missing_tks.update(missing_ticker_df[["name_show_on_MS", "Bloomberg Code_map"]])
        missing_tks["Bloomberg Code"] = missing_tks["Bloomberg Code_map"]

        df.set_index("Instr_long_name", drop=False, inplace=True)
        df.update(missing_tks["Bloomberg Code"])

        swap_df = missing_tks[missing_tks["Instr_Category"] == "SWAT"].copy()
        swap_df.set_index("name_show_on_MS", drop=False, inplace=True)
        swap_df.drop_duplicates(subset=["name_show_on_MS"], inplace=True)

        # Import MS swap, keep in mind later we need to automate file directary
        ms_cols_to_keep = [
            "Stock description",
            "ISIN",
            "Open Quantity",
            "Mark Price",
            "Mark FX",
            "Mark Notional",
        ]

        ms_swap_loc = ms_swap_lookup[suc_acc_name]
        try:
            ms_swap = pd.read_csv(ms_swap_loc[0], header=1)
        except:
            ms_swap = pd.read_csv(ms_swap_loc[1], header=1)

        ms_swap.dropna(subset=["Account Name"], inplace=True)
        ms_swap = ms_swap.loc[ms_swap["Leg Type"] == "Q", ms_cols_to_keep].copy()
        ms_swap.set_index("Stock description", drop=True, inplace=True)

        swap_df = swap_df.join(ms_swap, how="left")
        swap_df["Price"] = swap_df["Mark Price"] / swap_df["Mark FX"]
        rename_cols = {"Open Quantity": "Quantity", "Mark Notional": "Market_Value"}
        swap_df = swap_df.rename(columns=rename_cols)
        swap_df = swap_df.reindex(
            columns=["Instr_long_name", "ISIN", "Quantity", "Price", "Market_Value"]
        )
        swap_df.set_index("Instr_long_name", drop=True, inplace=True)

        #         df.update(swap_df)
        #         df.reset_index(drop=True,inplace=True)
        df.reset_index(drop=True, inplace=True)
        df_subset = df.loc[
            (df["Instr_Category"] == "SWAT")
            & (df["Stock_Type"] == "HOBI")
            & (df["Long_short"] == "RECU"),
            ["Instr_long_name", "ISIN", "Quantity", "Price", "Market_Value"],
        ].copy()
        df_subset.reset_index(drop=False, inplace=True)
        df_subset.set_index("Instr_long_name", drop=True, inplace=True)
        df_subset.update(swap_df)
        df_subset.set_index("index", drop=True, inplace=True)

        df.update(df_subset)

    #         df.loc[(df['Instr_Category']=='SWAT') & (df['Stock_Type']=='HOBI') & (df['Long_short']=='RECU'),:] = df.loc[(df['Instr_Category']=='SWAT') & (df['Stock_Type']=='HOBI') & (df['Long_short']=='RECU'),:].update(swap_df)
    #         df.reset_index(drop=True,inplace=True)
    return df


class vitruvius:

    #     #Class attribute
    deri_cols = [
        "Sub-Fund_long_name",
        "Sub-Fund_ccy",
        "Valuation_date",
        "Instr_Category",
        "Instr_long_name",
        "Instr_evaluation_ccy",
        "Bloomberg Code",
        "Stock_Type",
        "Long_short",
        "Price",
        "Market_Value",
        "Market_Value_in_Instr_CCY",
        "Quantity",
        "Market_Value_NAV_%",
        "contrepartie",
    ]

    def __init__(self, port):
        self.port = port
        self.fund_code = "000" + str(
            self.port["Fund_code"].unique()[0]
        )  # fund_code = Fund_code
        self.sub_code = "0" + str(
            self.port["Sub-Fund_Code"].unique()[0]
        )  # sub_code = Sub-Fund_Code
        self.fund_name = self.port["Sub-Fund_long_name"].unique()[
            0
        ]  # fund_name = Sub-fund_long_name
        self.ccy = self.port["Sub-Fund_ccy"].unique()[0]  # ccy = Sub-Fund_ccy
        self.nav_date = self.port["Valuation_date"].unique()[
            0
        ]  # nav_date = Valuation_date
        self.vmob_value = self.port.loc[
            self.port["Instr_Category"] == "VMOB", "Market_Value"
        ].sum()
        self.vmob_pct = self.port.loc[
            self.port["Instr_Category"] == "VMOB", "Market_Value_NAV_%"
        ].sum()
        self.aum = self.vmob_value / self.vmob_pct * 100

    # representation of class attributes
    def __repr__(self):
        rep = f"Fund Code: '{self.fund_code}', Sub Code: '{self.sub_code}', Fund Name: '{self.fund_name}', NAV Date: '{self.nav_date}' AUM: '{self.aum}'."
        return rep

    # def deri function which could call port dataframe based on their derivative classification (e.g. opti, futu, swat)
    def deri(self, deri_classification):
        # Check the derivative classification before carrying on with the call
        assert deri_classification in (
            "OPTI",
            "FUTU",
            "SWAT",
            "CAT",
        ), f"You entered '{deri_classification}', but derivative category can only be 'OPTI' or 'FUTU' or 'SWAT' or 'CAT'"

        #         deri_cols = ['Sub-Fund_long_name','Sub-Fund_ccy','Valuation_date','Instr_Category',
        #                      'Instr_long_name','Bloomberg Code','Stock_Type','Long_short','Price','Market_Value',
        #                      'Quantity','Market_Value_NAV_%','contrepartie']

        # return swap dataframe if any
        if deri_classification == "SWAT":
            deri_df = self.port.loc[
                (self.port["Instr_Category"] == deri_classification)
                & (self.port["Stock_Type"] == "HOBI")
                & (self.port["Long_short"] == "RECU"),
                self.deri_cols,
            ].copy()
            deri_df["Market_Value_NAV_%"] = (
                deri_df["Market_Value"] / self.aum * 100
            )  # recalculate swap mkt value % with new AUM.

        elif deri_classification == "OPTI":
            deri_df = self.port.loc[
                (self.port["Instr_Category"] == deri_classification)
                & (self.port["Stock_Type"] == "HOBI"),
                self.deri_cols,
            ].copy()

            deri_df["Delta"] = (
                deri_df["Market_Value"] / deri_df["Quantity"] / deri_df["Price"] / 100
            )

        elif deri_classification == "CAT":
            # cat_unique = ccy_hedging(self.port)
            df_copy = self.port.copy()
            cat_df = df_copy[
                (df_copy["Instr_Category"] == "CAT")
                & (df_copy["Sub-Fund_ccy"] != df_copy["Instr_evaluation_ccy"])
                & (~df_copy["Instr_long_name"].str.contains("G[1-9]$"))
                & (df_copy["Stock_Type"] == "HOBI")
            ].copy()
            # & (df_copy['Line_status']!='ACHLIG') & (df_copy['Line_status']!='VENLIG')].copy()
            cat_df_selected = cat_df.loc[
                :, ["Instr_long_name", "Market_Value", "Quantity", "Market_Value_NAV_%"]
            ].copy()
            cat_df_selected_groupby = cat_df_selected.groupby(
                by="Instr_long_name"
            ).sum()
            cat_unique = cat_df.drop_duplicates(subset="Instr_long_name").copy()
            cat_unique.set_index("Instr_long_name", drop=False, inplace=True)
            cat_unique.update(cat_df_selected_groupby)
            cat_unique.reset_index(drop=True, inplace=True)
            deri_df = cat_unique[self.deri_cols].copy()

        else:
            deri_df = self.port.loc[
                (self.port["Instr_Category"] == deri_classification)
                & (self.port["Stock_Type"] == "HOBI"),
                self.deri_cols,
            ].copy()

        # return option dataframe if any
        if deri_classification == "OPTI":
            deri_df["Delta"] = (
                deri_df["Market_Value"] / deri_df["Quantity"] / deri_df["Price"] / 100
            )
        else:
            deri_df["Delta"] = np.nan
        deri_cols_reindex = [
            "Sub-Fund_long_name",
            "Sub-Fund_ccy",
            "Valuation_date",
            "Instr_Category",
            "Instr_long_name",
            "Instr_evaluation_ccy",
            "Bloomberg Code",
            "Stock_Type",
            "Long_short",
            "Price",
            "Delta",
            "Market_Value",
            "Quantity",
            "Market_Value_NAV_%",
            "contrepartie",
        ]
        deri_df = deri_df.reindex(columns=deri_cols_reindex)

        return deri_df

    #######################################################################################################################
    def counterparty_FET(self):
        # pre-set FET discount parameter, can be changed in the future
        FET_param = 0.01 * 0.2

        cat_df = self.port.loc[self.port["Instr_Category"] == "CAT"].copy()
        cat_df["Share_Class"] = np.nan
        cat_df.loc[
            cat_df["Instr_evaluation_ccy"] != cat_df["Sub-Fund_ccy"], "Share_Class"
        ] = cat_df.loc[
            cat_df["Instr_evaluation_ccy"] != cat_df["Sub-Fund_ccy"],
            "Instr_evaluation_ccy",
        ]

        # define share classes
        share_class_map = cat_df.loc[
            cat_df["Instr_evaluation_ccy"] != cat_df["Sub-Fund_ccy"],
            ["Instr_long_name", "Share_Class"],
        ].copy()
        share_class_map.drop_duplicates(inplace=True)
        share_class_map.set_index("Instr_long_name", drop=True, inplace=True)

        # update share class names
        cat_df.set_index("Instr_long_name", drop=False, inplace=True)
        cat_df.update(share_class_map)
        cat_df = cat_df.reset_index(drop=True)

        # find notional amount of hedging
        cols_to_keep = [
            "Share_Class",
            "Instr_long_name",
            "Instr_evaluation_ccy",
            "Market_Value",
            "Market_Value_in_Instr_CCY",
            "Market_Value_NAV_%",
        ]
        #         notional_cat = cat_df.loc[cat_df['Price']==0,cols_to_keep].groupby(by=['Share_Class','Instr_long_name','Instr_evaluation_ccy']).sum()
        notional_cat = (
            cat_df.loc[
                (cat_df["Stock_Type"] == "HOBI")
                & (cat_df["Sub-Fund_ccy"] == cat_df["Instr_evaluation_ccy"]),
                cols_to_keep,
            ]
            .groupby(by=["Share_Class", "Instr_long_name", "Instr_evaluation_ccy"])
            .sum()
        )

        # find p&l amount of hedging
        pnl_cat = (
            cat_df.loc[cat_df["Stock_Type"] == "AD1", cols_to_keep]
            .groupby(by=["Share_Class", "Instr_long_name", "Instr_evaluation_ccy"])
            .sum()
        )

        # join FET and FET pnl in one table
        notional_cat = notional_cat.join(pnl_cat, rsuffix="_pnl")
        notional_cat.loc[("Netted Notional", " ", " ")] = notional_cat.sum()

        # calculate total netted notional amount of FET, if total netted pnl is negative, we set pnl value to zero,
        # because negative pnl means we owe money to countryparty, therefore, we counterparty risk
        notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value"] = abs(
            notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value"]
        )
        notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_NAV_%"] = abs(
            notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_NAV_%"]
        )
        notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_pnl"] = max(
            0, notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_pnl"]
        )
        notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_NAV_%_pnl"] = max(
            0, notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_NAV_%_pnl"]
        )

        # calculate FET commitment
        notional_cat.loc[("FET Commitment", " ", " ")] = np.nan
        notional_cat.loc[("FET Commitment", " ", " ")]["Market_Value"] = (
            notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value"] * FET_param
        )
        notional_cat.loc[("FET Commitment", " ", " ")]["Market_Value_NAV_%"] = (
            notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_NAV_%"]
            * FET_param
        )
        notional_cat.loc[("FET Commitment", " ", " ")]["Market_Value_pnl"] = (
            notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_pnl"]
            * FET_param
        )
        notional_cat.loc[("FET Commitment", " ", " ")]["Market_Value_NAV_%_pnl"] = (
            notional_cat.loc[("Netted Notional", " ", " ")]["Market_Value_NAV_%_pnl"]
            * FET_param
        )

        return notional_cat

    ######################################################################################################################
    def Quintet_balance(self):
        return self.port.loc[
            self.port["Instr_long_name"] == "Quintet Private Bank (Eu) SA",
            "Market_Val+Accr_Int_NAV_%",
        ].sum()

    ######################################################################################################################
    def morganstanley_counterparty_risk(self):

        #         deri_cols = ['Sub-Fund_long_name','Sub-Fund_ccy','Valuation_date','Instr_Category',
        #              'Instr_long_name','Bloomberg Code','Stock_Type','Long_short','Price','Market_Value',
        #              'Quantity','Market_Value_NAV_%','contrepartie']

        self.port["contrepartie"] = self.port["contrepartie"].str.lower()
        cond_1 = self.port["contrepartie"].str.contains("morgan stanley", na=False)
        cond_2 = self.port["Line_status"] == "PROPRE"
        cond_3 = self.port["Stock_Type"] == "AD1"
        cond_4 = self.port["Instr_Category"] == "TRES"
        cond_5 = self.port["Market_Value"] != 0
        cond_6 = self.port["Instr_Category"] != "TRES"

        ms_margin = self.port.loc[cond_1 & cond_2 & cond_3 & cond_4, :]
        ms_pnl = self.port.loc[cond_1 & cond_3 & cond_5 & cond_6, :]
        ms_counterparty_risk = pd.concat([ms_margin, ms_pnl])
        ms_counterparty_sum = max(ms_counterparty_risk["Market_Value"].sum(), 0)
        ms_counterparty_sum_pct = max(
            ms_counterparty_risk["Market_Value_NAV_%"].sum(), 0
        )
        ms_counterparty_risk.loc["tot_MS_Counterparty_risk"] = np.nan
        ms_counterparty_risk.loc[
            "tot_MS_Counterparty_risk", "Market_Value"
        ] = ms_counterparty_sum
        ms_counterparty_risk.loc[
            "tot_MS_Counterparty_risk", "Market_Value_NAV_%"
        ] = ms_counterparty_sum_pct

        ms_counterparty_risk = ms_counterparty_risk[self.deri_cols]

        return ms_counterparty_risk

    ################################################################################################################
    def type_valeur(self):
        # define type valeur classification map
        type_valeur_dict = {
            "type_valeur": [
                "1010",
                "1383",
                "1090",
                "1201",
                "1341",
                "1383",
                "1030",
                "1370",
                "1374",
                "1390",
                "1397",
                "2171",
            ],
            "type_des": [
                "Equity",
                "REITS",
                "ADR",
                "Warrent",
                "UCI Open-End Funds",
                "Non-Traded REIT",
                "Prefered Share",
                "Closed-End Fund",
                "Closed-End Fund - Mixed",
                "ETF",
                "InvCo",
                "P-Notes",
            ],
        }

        # convert to pandas dataframe
        type_valeur_df = pd.DataFrame.from_dict(type_valeur_dict)
        type_valeur_df.set_index("type_valeur", drop=True, inplace=True)

        # extract essential columns
        subport = self.port[
            ["type_valeur", "Market_Value", "Market_Value_NAV_%"]
        ].copy()
        subport.dropna(subset=["type_valeur"], inplace=True)
        subport["type_valeur"] = subport["type_valeur"].astype(int)
        subport["type_valeur"] = subport["type_valeur"].astype(str)
        port_type = subport.groupby(by=["type_valeur"]).sum()

        # left joined type_valeur_df with vitruvius data
        type_valeur_df = type_valeur_df.join(port_type, how="left")
        type_valeur_df.sort_values(by=["Market_Value"], ascending=False, inplace=True)
        type_valeur_df

        # if the portfolio has swap positions, also need to extract the rows
        swap_df = self.port.loc[
            (self.port["Instr_Category"] == "SWAT")
            & (self.port["Stock_Type"] == "HOBI")
            & (self.port["Long_short"] == "RECU"),
            self.deri_cols,
        ].copy()
        swap_df["Market_Value_NAV_%"] = swap_df["Market_Value"] / self.aum * 100

        if len(swap_df) > 0:
            type_valeur_swap = swap_df[
                ["Instr_Category", "Market_Value", "Market_Value_NAV_%"]
            ].copy()
            type_valeur_swap["type_valeur"] = -1
            type_valeur_swap = type_valeur_swap.rename(
                columns={"Instr_Category": "type_des"}
            )
            type_valeur_swap = type_valeur_swap.reindex(
                columns=[
                    "type_des",
                    "Market_Value",
                    "Market_Value_NAV_%",
                    "type_valeur",
                ]
            )
            type_valeur_swap = type_valeur_swap.groupby(
                by=["type_valeur", "type_des"]
            ).sum()
            type_valeur_swap.reset_index(drop=False, inplace=True)
            type_valeur_swap.set_index("type_valeur", drop=True, inplace=True)
        else:
            type_valeur_swap = pd.DataFrame(
                columns=[
                    "type_des",
                    "Market_Value",
                    "Market_Value_NAV_%",
                    "type_valeur",
                ]
            )

        # combbine swap into the type_valeur_df
        type_valeur_df = pd.concat([type_valeur_df, type_valeur_swap])
        type_valeur_df.sort_values(by=["Market_Value"], ascending=False, inplace=True)

        # calculate total equity exposure and cash level, assign aum to last row
        type_valeur_df.dropna(subset=["Market_Value"], inplace=True)
        type_valeur_df.loc["Total Equity Exposure"] = type_valeur_df.sum()
        type_valeur_df.loc["Total Equity Exposure", "type_des"] = np.nan
        type_valeur_df.loc["Cash"] = np.nan
        type_valeur_df.loc["NAV"] = np.nan
        type_valeur_df.loc["NAV", "Market_Value"] = self.aum
        type_valeur_df.loc["NAV", "Market_Value_NAV_%"] = 100
        type_valeur_df.loc["Cash", "Market_Value"] = (
            type_valeur_df.loc["NAV", "Market_Value"]
            - type_valeur_df.loc["Total Equity Exposure", "Market_Value"]
        )
        type_valeur_df.loc["Cash", "Market_Value_NAV_%"] = (
            (self.aum - type_valeur_df.loc["Total Equity Exposure", "Market_Value"])
            / self.aum
            * 100
        )

        return type_valeur_df

    def shareclass_hedging(self):
        df_copy = self.port.copy()
        cat_df = df_copy[
            (df_copy["Instr_Category"] == "CAT")
            & (df_copy["Sub-Fund_ccy"] != df_copy["Instr_evaluation_ccy"])
            & (df_copy["Instr_long_name"].str.contains("G[1-9]$"))
            & (df_copy["Stock_Type"] == "HOBI")
        ].copy()
        # & (df_copy['Line_status']!='ACHLIG') & (df_copy['Line_status']!='VENLIG')].copy()
        cat_df_selected = cat_df.loc[
            :, ["Instr_long_name", "Market_Value", "Quantity", "Market_Value_NAV_%"]
        ].copy()
        cat_df_selected_groupby = cat_df_selected.groupby(by="Instr_long_name").sum()
        cat_unique = cat_df.drop_duplicates(subset="Instr_long_name").copy()
        cat_unique.set_index("Instr_long_name", drop=False, inplace=True)
        cat_unique.update(cat_df_selected_groupby)
        cat_unique.reset_index(drop=True, inplace=True)
        deri_df = cat_unique[self.deri_cols].copy()
        return deri_df

    ##############################################


# Create a child class called 'master' which will inheritate all the methonds and attributes from 'vitrvius' class
class master(vitruvius):

    deri_cols_master = [
        "Sub-Fund_long_name",
        "Sub-Fund_ccy",
        "Valuation_date",
        "Instr_Category",
        "Instr_long_name",
        "Instr_evaluation_ccy",
        "Maturity_date",
        "Bloomberg Code",
        "Stock_Type",
        "Long_short",
        "Price",
        "Market_Value",
        "Market_Value_in_Instr_CCY",
        "Quantity",
        "Market_Value_NAV_%",
        "contrepartie",
    ]

    def __init__(self, port):
        """The super() function in Python makes class inheritance more manageable and extensible. 
        The function returns a temporary object that allows reference to a parent class by the keyword super."""
        super().__init__(port)

    # get AP-Account Payables and AR-Account Receivables
    def APAR(self):
        cond_1 = self.port["Instr_Category"] == "TRES"
        cond_2 = self.port["Instr_long_name"].str.contains("Payable", case=False)
        cond_3 = self.port["Instr_long_name"].str.contains("Receivable", case=False)
        cond_4 = self.port["Instr_evaluation_ccy"] != self.port["Sub-Fund_ccy"]
        APAR = self.port.loc[cond_1 & cond_4 & (cond_2 | cond_3), self.deri_cols_master]
        APAR.loc[
            APAR["Instr_long_name"] == "Payable/treasury acc", "Instr_long_name"
        ] = "Payables"
        APAR.loc[
            APAR["Instr_long_name"] == "Payable/redemptions", "Instr_long_name"
        ] = "Payables"
        APAR.loc[
            APAR["Instr_long_name"] == "Receivable/subscrip.", "Instr_long_name"
        ] = "Receivables"
        APAR.loc[
            APAR["Instr_long_name"] == "Receivable/treas acc", "Instr_long_name"
        ] = "Receivables"
        return APAR

    # get Quintet balance in local currency for each share class
    def Quintet_Balance(self):
        cond_1 = self.port["Instr_Category"] == "TRES"
        cond_2 = self.port["Instr_long_name"].str.contains(
            "Quintet Private Bank", case=False
        )
        cond_3 = self.port["Instr_evaluation_ccy"] != self.port["Sub-Fund_ccy"]
        cond_4 = self.port["Line_status"] == "PROPRE"
        balance_lcl = self.port.loc[
            cond_1 & cond_2 & cond_3 & cond_4, self.deri_cols_master
        ]
        return balance_lcl

    def shareclass_hedging(self):
        df_copy = self.port.copy()
        cat_df = df_copy[
            (df_copy["Instr_Category"] == "CAT")
            & (df_copy["Sub-Fund_ccy"] != df_copy["Instr_evaluation_ccy"])
            & (df_copy["Instr_long_name"].str.contains("G[1-9]$"))
            & (df_copy["Stock_Type"] == "HOBI")
        ].copy()
        # & (df_copy['Line_status']!='ACHLIG') & (df_copy['Line_status']!='VENLIG')].copy()
        cat_df_selected = cat_df.loc[
            :, ["Instr_long_name", "Market_Value", "Quantity", "Market_Value_NAV_%"]
        ].copy()
        cat_df_selected_groupby = cat_df_selected.groupby(by="Instr_long_name").sum()
        cat_unique = cat_df.drop_duplicates(subset="Instr_long_name").copy()
        cat_unique.set_index("Instr_long_name", drop=False, inplace=True)
        cat_unique.update(cat_df_selected_groupby)
        cat_unique.reset_index(drop=True, inplace=True)
        deri_df = cat_unique[self.deri_cols_master].copy()
        return deri_df


def file_directory_generator(filename, report_date="", sub_acc=""):
    folder_dict = {
        "ffnav": [
            "G:/network users/SICAV/EFA-Daily-FFNAV/Vitruvius_FFNAV/",
            "ffnav1_*_*_" + report_date + "_*_1.csv",
        ],
        "summarySheet": [
            "G:/network users/SICAV/Monthly Letters/Structure Report Project/",
            "Vitruvius Summary Sheet.xlsx",
        ],
        "ffpos": [
            "G:/network users/SICAV/EFA-Daily-Position-Net-Assets/FFPOS/",
            "/ffpos1_*_*_" + report_date + "_*_1.csv",
        ],
        "NTAP": [
            "G:/network users/SICAV/EFA-Daily-NTAP/",
            "NTAP Estimation of fund payable and receivable_*_"
            + report_date
            + "_*.xls",
        ],
        "template": [
            "G:/network users/Sni/Daily Check SICAV/",
            "Hedging Monitor Template.xlsx",
        ],
        "report_to": [
            "G:/network users/SICAV/EUR Hedge/New Hedging Monitor/",
            f"Vit Hedging Monitor_{report_date}.xlsx",
        ],
    }

    return folder_dict[filename][0] + sub_acc + folder_dict[filename][1]



# generate aum table for all the accouns from the ffnav sheet
def generate_aum_table(ffnav_file_path, report_date_strf):
    assert (
        len(glob.glob(ffnav_file_path)) > 0
    ), f"The FFNAV file for {report_date_strf} is not in the folder, could you double check!!!"

    ffnav_fileloc = glob.glob(ffnav_file_path)[0]
    ffnav_raw = pd.read_csv(ffnav_fileloc)
    ffnav_raw["Sub-fund_code"] = "0" + ffnav_raw["Sub-fund_code"].astype(str)
    ffnav = ffnav_raw.loc[
        ffnav_raw["Sub-fund_currency"] == ffnav_raw["CCY_NAV_share"],
        ["Sub-fund_code", "Valuation_date", "Net_assets_share_type"],
    ].copy()
    aum_df = ffnav.groupby(by=["Sub-fund_code", "Valuation_date"]).sum()
    aum_df.reset_index(drop=False, inplace=True)
    aum_df.set_index("Sub-fund_code", drop=True, inplace=True)
    return aum_df, ffnav_raw


def generate_summary_table(aum_df, file_path):
    summary_file_path = file_path
    summary_file_path = file_directory_generator("summarySheet")
    summary_df = pd.read_excel(summary_file_path, sheet_name="Port_summary")
    summary_df["account_code"] = "0" + summary_df["account_code"].astype(str)
    summary_df.set_index("account_code", drop=True, inplace=True)

    # Join aum table with summary tabe and calculate % allocation to each sub-acc (if it exists).
    vit_aum = summary_df.join(aum_df)
    vit_aum["Master_AUM"] = np.nan

    for shortName in vit_aum["portfolio"].unique():
        cond_1 = vit_aum["sheetname"] == "Master"
        cond_2 = vit_aum["portfolio"] == shortName

        if len(vit_aum[cond_1 & cond_2]) == 0:
            master_aum = vit_aum.loc[cond_2, "Net_assets_share_type"].get(0)
        else:
            master_aum = vit_aum.loc[cond_1 & cond_2, "Net_assets_share_type"].get(0)

        vit_aum.loc[cond_2, "Master_AUM"] = master_aum

    vit_aum["subAcc_%"] = vit_aum["Net_assets_share_type"] / vit_aum["Master_AUM"] * 100

    return vit_aum


################################
def compute_fxHedging_APAR_Cash_hedgingMonitor(ffpos_file_map, ffnav_raw):
    master_ffpos_dir = []
    for master_acc in ffpos_file_map["portfolio"].unique():
        cond_1 = ffpos_file_map["sheetname"] == "Master"
        cond_2 = ffpos_file_map["portfolio"] == master_acc

        if len(ffpos_file_map[cond_1 & cond_2]) == 0:
            ffpos_dir = ffpos_file_map.loc[cond_2, "ffpos_dir"].get(0)
        else:
            ffpos_dir = ffpos_file_map.loc[cond_1 & cond_2, "ffpos_dir"].get(0)

        master_ffpos_dir.append(ffpos_dir)
    # return master_ffpos_dir

    shareClass_hedging = pd.DataFrame()
    APAR = pd.DataFrame()
    Quintet_cash = pd.DataFrame()
    for each_master in master_ffpos_dir:
        ffpos = pd.read_csv(each_master, encoding="cp1252")
        vit = master(ffpos)
        # gettting share class hedging information
        fx_hedging = vit.shareclass_hedging()
        fx_hedging["account_code"] = vit.sub_code
        fx_hedging["join_index"] = (
            fx_hedging["account_code"] + "_" + fx_hedging["Instr_evaluation_ccy"]
        )
        shareClass_hedging = pd.concat([shareClass_hedging, fx_hedging])

        # getting payable and receivable information from masteraccount
        payable_receivable = vit.APAR()
        payable_receivable["account_code"] = vit.sub_code
        payable_receivable["join_index"] = (
            payable_receivable["account_code"]
            + "_"
            + payable_receivable["Instr_evaluation_ccy"]
        )
        APAR = pd.concat([APAR, payable_receivable])

        # getting Quintet bank balance in each sharec class from masteraccount
        Quintet_balance = vit.Quintet_Balance()
        Quintet_balance["account_code"] = vit.sub_code
        Quintet_balance["join_index"] = (
            Quintet_balance["account_code"]
            + "_"
            + Quintet_balance["Instr_evaluation_ccy"]
        )
        Quintet_cash = pd.concat([Quintet_cash, Quintet_balance])

    # get FX Forward contracts for share class
    fx_amount = (
        shareClass_hedging[["join_index", "Maturity_date", "Quantity"]]
        .groupby(by=["join_index", "Maturity_date"])
        .sum()
    )
    fx_amount.rename(columns={"Quantity": "FX_FWD"}, inplace=True)
    fx_amount.reset_index(drop=False, inplace=True)
    fx_amount.set_index("join_index", drop=True, inplace=True)
    fx_amount = fx_amount.reindex(columns=["FX_FWD", "Maturity_date"])

    # get subs/reds payables and receivables from ffpos master account
    APAR_copy = APAR[["join_index", "Instr_long_name", "Quantity"]].copy()
    Pay_Rec = pd.pivot_table(
        data=APAR_copy,
        values="Quantity",
        index="join_index",
        columns="Instr_long_name",
        aggfunc=np.sum,
    )
    col_to_rename = {
        "Payable/redemptions": "Payables",
        "Receivable/subscrip.": "Receivables",
    }
    Pay_Rec.rename(columns=col_to_rename, inplace=True)

    # get Quintet balance from ffpos account
    balance = (
        Quintet_cash[["join_index", "Market_Value_in_Instr_CCY"]]
        .groupby(by=["join_index"])
        .sum()
    )
    balance.rename(
        columns={"Market_Value_in_Instr_CCY": "Quintet Balance"}, inplace=True
    )

    cols_to_keep = [
        "Sub-fund_code",
        "Share_code",
        "Valuation_date",
        "Sub-fund_currency",
        "Net_assets_share_type",
        "CCY_NAV_share",
        "Sub_fund_long_name",
    ]

    groupby_cols = [
        "Sub_fund_long_name",
        "Sub-fund_code",
        "Sub-fund_currency",
        "Valuation_date",
        "CCY_NAV_share",
    ]

    shareClass_needTo_hedge = ffnav_raw.loc[
        ffnav_raw["Sub-fund_currency"] != ffnav_raw["CCY_NAV_share"], cols_to_keep
    ].copy()
    hedgingMonitor = shareClass_needTo_hedge.groupby(by=groupby_cols).sum()
    hedgingMonitor.reset_index(drop=False, inplace=True)
    hedgingMonitor["join_index"] = (
        hedgingMonitor["Sub-fund_code"] + "_" + hedgingMonitor["CCY_NAV_share"]
    )
    hedgingMonitor.set_index(["join_index"], inplace=True, drop=True)

    hedgingMonitor = hedgingMonitor.join([fx_amount, Pay_Rec, balance])

    return fx_amount, Pay_Rec, balance, hedgingMonitor


def sub_red_table(nav_date):
    # NTAP_dir = "G:/network users/SICAV/EFA-Daily-NTAP/"
    # NTAP_pattern = (
    #     "NTAP Estimation of fund payable and receivable_*_" + nav_date + "_*.xls"
    # )
    NTAP_file_path = file_directory_generator("NTAP", nav_date)
    sub_red_file = glob.glob(NTAP_file_path)
    # sub_red_file = glob.glob(NTAP_dir + NTAP_pattern)
    assert (
        len(sub_red_file) > 0
    ), f"NTAP payable and receivable {nav_date} is not in the folder, could you double check!!!"
    NTAP_df = pd.read_excel(sub_red_file[0])
    NTAP_df["Sub-fund ID"] = NTAP_df["Sub-fund ID"].str.replace("'", "")
    NTAP_df["join_index"] = NTAP_df["Sub-fund ID"] + "_" + NTAP_df["Unit Price Ccy"]
    NTAP_df["Applicable NAV date"] = NTAP_df["Applicable NAV date"].dt.strftime(
        "%Y-%m-%d"
    )
    applicable_nav_date = NTAP_df["Applicable NAV date"].unique()[0]
    NTAP_df_pivot = pd.pivot_table(
        data=NTAP_df,
        index="join_index",
        values=["Total Receivable", "Total Payable"],
        aggfunc=np.sum,
    )

    NTAP_df_pivot = NTAP_df_pivot.rename(
        columns={
            "Total Payable": f"Redemption {applicable_nav_date}",
            "Total Receivable": f"Subscription {applicable_nav_date}",
        }
    )

    return NTAP_df_pivot, applicable_nav_date


def new_cols_to_assign(nav_date_today,nav_date_tmw):
    new_cols = [ "Sub_fund_long_name",
            "Sub-fund_code",
            "Sub-fund_currency",
            "Valuation_date",
            "CCY_NAV_share",
            "Net_assets_share_type",
            "FX_FWD",
            "Maturity_date",
            "Payables",
            "Receivables",
            "Quintet Balance",
            f"Redemption {nav_date_today}",
            f"Subscription {nav_date_today}",
            f"Redemption {nav_date_tmw}",
            f"Subscription {nav_date_tmw}",
            ]
    return new_cols

def ult_col_map_hedgingMonitor():
    ult_col_map = {"Sub_fund_long_name": "Fund name",
                "Sub-fund_code": "Fund Code",
                "Sub-fund_currency": "Fund CCY",
                "Valuation_date": "NAV Date",
                "CCY_NAV_share": "Share Class CCY",
                "Net_assets_share_type": "Net Asset (Sh Class)",
                "FX_FWD": "FWD Contracts",
                "Maturity_date": "FWD Maturity",
                }
    return ult_col_map



def hedging_amount(x):
    if x.loc['New Hedging Status (Limit 95%-105%)']=='Underhedging':
        return x.loc['Net Asset (adj.subs/reds=T&T+1)'] - x.loc['FWD Contracts']
    elif x.loc['New Hedging Status (Limit 95%-105%)']=='Overhedging':
        return x.loc['FWD Contracts'] - x.loc['Net Asset (adj.subs/reds=T&T+1)']
    else:
        pass

def hedging_status(x):
    if x>1.05:
        return 'Overhedging'
    elif x<0.95:
        return 'Underhedging'
    else:
        return 'Normal'

def hedging_calculation(hedgingMonitor,nav_date_today,nav_date_tmw):
    fullTable = hedgingMonitor.copy()
    fullTable = fullTable.fillna(0)
    fullTable['Cash Balance (base case)'] = fullTable['Payables'] + fullTable['Receivables'] + fullTable['Quintet Balance'] \
                                            + fullTable[f'Redemption {nav_date_today}'] + fullTable[f'Subscription {nav_date_today}']
    fullTable['Hedging Ratio (base case)'] = fullTable['FWD Contracts'] / fullTable['Net Asset (Sh Class)']

    fullTable['Hedging Diff. (over+/under-)'] = fullTable['FWD Contracts'] - fullTable['Net Asset (Sh Class)']

    fullTable['Calculation Section'] = np.nan
    fullTable['Hedging Status(Limit 95%-105%)'] = fullTable['Hedging Ratio (base case)'].apply(hedging_status)

    fullTable['Heging Ratio Modification Section'] = np.nan
    fullTable['Est. Daily Return (manual input)'] = 0.01
    fullTable['Net Asset (adj.subs/reds=T)'] = fullTable['Net Asset (Sh Class)'] * (1 + fullTable['Est. Daily Return (manual input)']) \
                                                + fullTable[f'Subscription {nav_date_today}'] + fullTable[f'Redemption {nav_date_today}']
    fullTable['Hedging Ratio (adj.subs/reds=T)'] = fullTable['FWD Contracts'] / fullTable['Net Asset (adj.subs/reds=T)']                               
    fullTable['Net Asset (adj.subs/reds=T&T+1)'] = fullTable['Net Asset (adj.subs/reds=T)'] + fullTable[f'Subscription {nav_date_tmw}'] + fullTable[f'Redemption {nav_date_tmw}']
    fullTable['Hedging Ratio (adj.subs/reds=T&T+1)'] = fullTable['FWD Contracts'] / fullTable['Net Asset (adj.subs/reds=T&T+1)']
    fullTable['New Hedging Status (Limit 95%-105%)'] = fullTable['Hedging Ratio (adj.subs/reds=T&T+1)'].apply(hedging_status)

    fullTable['FWD Adjustment (if needed)'] = np.nan
    fullTable['If Underhedging'] = ' Buy ' + fullTable['Share Class CCY'] + ' Sell ' + fullTable['Fund CCY']

    fullTable['Execution Amount for underhedging'] = fullTable.apply(hedging_amount,axis=1)
    fullTable['If Overhedging'] = ' Sell ' + fullTable['Share Class CCY'] + ' Buy ' + fullTable['Fund CCY']
    fullTable['Execution Amount for Overhedging'] = fullTable.apply(hedging_amount,axis=1)

    fullTable['Fund name'] = fullTable['Fund name'].str.title()
    fullTable.set_index(['Fund name','Fund Code','Fund CCY','NAV Date','Share Class CCY'],inplace=True)
    fullTable_T = fullTable.T.copy()
    return fullTable_T


def style_negative(v,prop=''):
    return prop if v<0 else None

def format_table(fullTable_T,nav_date_today,nav_date_tmw):
    fullTable_a = fullTable_T.copy()
    fullTable_a = fullTable_a.replace(0,np.nan)
    fullTable_style = fullTable_a.style.applymap(style_negative,prop='color:red;',subset=pd.IndexSlice[['Payables',f'Redemption {nav_date_today}',f'Redemption {nav_date_tmw}'],:])
    fullTable_style.format(precision=0,na_rep="",thousands=",")
    fullTable_style.format(formatter='{:.1%}',subset=pd.IndexSlice[['Hedging Ratio (base case)',
                                                                    'Est. Daily Return (manual input)',
                                                                'Hedging Ratio (adj.subs/reds=T)',
                                                                'Hedging Ratio (adj.subs/reds=T&T+1)'],:])
    return fullTable_style
