CREATE TABLE [dbo].[po_details] (
    [PO_NO]              INT             NOT NULL,
    [PO_DATE]            DATE            NULL,
    [PO_PART_NO]         VARCHAR (50)    NULL,
    [PO_DESC]            VARCHAR (255)   NULL,
    [PO_PART_COND]       VARCHAR (100)   NULL,
    [PO_PART_QUANTITY]   INT             NULL,
    [PO_PART_HSN]        VARCHAR (20)    NULL,
    [PO_GST_NO]          VARCHAR (20)    NULL,
    [PO_GST_PERCENTAGE]  DECIMAL (5, 2)  NULL,
    [PO_PART_UNIT_PRICE] DECIMAL (10, 2) NULL,
    [PO_PART_AMOUNT]     DECIMAL (12, 2) NULL,
    PRIMARY KEY CLUSTERED ([PO_NO] ASC)
);


GO

