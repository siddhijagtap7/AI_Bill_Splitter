import  pandas as pd    

def item_consumer(mat,item,person):
    """
    Marks that a particular person is consuming a particular item.
    Args:
        mat (list of list of int): The consumption matrix.
        item (int): The index of the item.
        person (int): The index of the person.
        Returns:
        list of list of int: The updated consumption matrix.
    """
    if(mat[item][person] == 0):
        mat[item][person] = 1
    return mat


def get_individual_prices(mat, df_items, df_price):
    """
    get_individual_prices calculates the amount each person has to pay based on the consumption matrix, item prices, quantities, and GST.
    Args:
        mat (list of list of int): The consumption matrix where mat[i][j] is 1 if person j consumes item i, else 0.
        df_items (pd.DataFrame): DataFrame containing 'Items', 'Quantity', and 'Prices' columns.
        df_price (pd.DataFrame): DataFrame containing 'Total', 'CGST', and 'SGST' columns.
    Returns:
        pd.DataFrame: A DataFrame where each cell [i][j] represents the amount person j has to pay for item i.
    """
    df_items['Quantity'] = pd.to_numeric(df_items['Quantity'], errors='coerce').fillna(1).astype(int)
    rows = len(mat)
    cols = len(mat[0])
    price = []
    total_gst = df_price['CGST'][0] + df_price['SGST'][0]

    for i in range(rows):
        counter = 0
        for j in range(cols):
            if mat[i][j] == 1:
                counter += 1
                
        # calculate the total price for the item (including quantity and GST)
        total_item_price = (df_items['Prices'][i] * df_items['Quantity'][i])
        gst_amt = total_item_price * total_gst / 100
        split_price = (total_item_price + gst_amt) / counter if counter > 0 else 0
        price.append(split_price)

    # update the matrix with the calculated split prices
    for i in range(rows):
        for j in range(cols):
            if mat[i][j] == 1:
                mat[i][j] = price[i]

    amt = pd.DataFrame(mat).round(2)
    return amt