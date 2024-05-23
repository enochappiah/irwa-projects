vendors_dict = {
    "https://www.mybobs.com/": 
    {
        "search": "/html/body/bobs-app-root/cx-storefront/header/cx-page-layout[1]/cx-page-slot[7]/bobs-header-search-box-hybris/div/bobs-pop-out/div/div/form/input",
        "product-grid": "/html/body/bobs-app-root/cx-storefront/main/cx-page-layout/cx-page-slot/bobs-brx/div/br-page/div/div[1]/div[2]/div/div/bobs-brx-product-list/bobs-product-scroll/bobs-plp-list-section/div/bobs-product-grid",
        "product-cards-tag": "bobs-brx-product-card",
        "product-id-class": "bobs-product-card-dynamic-load",
        "description-div": '//*[@id="bobs-product-details-tabs"]/bobs-tabs/bobs-tab[1]/div/bobs-product-details-tab-content/div[1]/div[1]/span[2]',

    },
    
    "https://www.bedbathandbeyond.com/":
    {
        "search": '//*[@id="ostk-search-combobox"]/input',
        "product-grid": '//*[@id="products"]',
        "product-cards-class": 'productTile_productTile__fCG1W',
        "product-link-class": 'productTile_link__zHGHe',
        "product-details-class": 'tileContent productTile_content__Zab3W', 
        "upper-price-container-class": 'priceContainer price_container__jbAh_',
        "inner-price-container-class": 'price_currentPriceContainer__aI9hY',
        "price-element-class": 'currentPrice price_price__RsJly price_sale__nO5AK',
        "product-name-class": 'title_wrapper__NBeDj',
        'description-div': '//*[@id="description-height"]/div[1]/div[2]/p[1]'

    },
    "https://www.wayfair.com/":
    {
        "search": '//*[@id="textInput-:R79557qja:"]',
        "product-grid": '//*[@id="searchResults"]',
        "product-cards-class": "_6o3atz4v _6o3atz5h _6o3atzl drvwgb7 drvwgb8 drvwgbb drvwgbe drvwgbd drvwgbh drvwgbk drvwgb1",
        "product-name-class": "ProductCardstyles__ProductName-sc-1j5v8b6-1",
        "product-price-class": "ProductCardstyles__PriceText-sc-1j5v8b6-6",
        "product-link-class": "ProductCardstyles__ProductCardLink-sc-1j5v8b6-3",
        "description-div": '//*[@id="CollapsePanel-0"]/div/div/div/div[1]/div/div/div',
    }
    }