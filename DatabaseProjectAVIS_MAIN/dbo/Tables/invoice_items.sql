CREATE TABLE [dbo].[invoice_items] (
    [ITEM_ID]     INT           IDENTITY (1, 1) NOT NULL,
    [INVOICE_NO]  VARCHAR (50)  NULL,
    [PART_NO]     VARCHAR (50)  NULL,
    [DESCRIPTION] VARCHAR (255) NULL,
    [CONDITION]   VARCHAR (50)  NULL,
    [QTY]         INT           NULL,
    [HSN]         VARCHAR (20)  NULL,
    [UNIT_PRICE]  FLOAT (53)    NULL,
    [AMOUNT]      FLOAT (53)    NULL,
    PRIMARY KEY CLUSTERED ([ITEM_ID] ASC)
);


GO

