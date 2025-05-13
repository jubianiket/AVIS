CREATE TABLE [dbo].[quote_details] (
    [QUOTE_NO]              INT             NOT NULL,
    [QUOTE_DATE]            DATE            NULL,
    [QUOTE_PART_NO]         VARCHAR (50)    NULL,
    [QUOTE_DESC]            VARCHAR (255)   NULL,
    [QUOTE_PART_COND]       VARCHAR (100)   NULL,
    [QUOTE_PART_QUANTITY]   INT             NULL,
    [QUOTE_PART_HSN]        VARCHAR (20)    NULL,
    [QUOTE_GST_NO]          VARCHAR (20)    NULL,
    [QUOTE_GST_PERCENTAGE]  DECIMAL (5, 2)  NULL,
    [QUOTE_PART_UNIT_PRICE] DECIMAL (10, 2) NULL,
    [QUOTE_PART_AMOUNT]     DECIMAL (12, 2) NULL,
    PRIMARY KEY CLUSTERED ([QUOTE_NO] ASC)
);


GO

