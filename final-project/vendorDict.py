vendors_dict = {
    "https://www.mybobs.com/": 
    {
        "search": "/html/body/bobs-app-root/cx-storefront/header/cx-page-layout[1]/cx-page-slot[7]/bobs-header-search-box-hybris/div/bobs-pop-out/div/div/form/input",
        "product-grid": "/html/body/bobs-app-root/cx-storefront/main/cx-page-layout/cx-page-slot/bobs-brx/div/br-page/div/div[1]/div[2]/div/div/bobs-brx-product-list/bobs-product-scroll/bobs-plp-list-section/div/bobs-product-grid",
        "product-cards-tag": "bobs-brx-product-card",
        "product-id-class": "bobs-product-card-dynamic-load",
        "description-div": '//*[@id="bobs-product-details-tabs"]/bobs-tabs/bobs-tab[1]/div/bobs-product-details-tab-content/div[1]/div[1]/span[2]',

    },
    "https://www.ashleyfurniture.com/": 
    {
        "search": '//*[@id="search-container"]/wc-search ', #//*[@id="search-form"]/input
        "product-grid": '//*[@id="search-result-items"]',
        "product-cards-tag": "product-tile",
        "product-name-attribute": "data-cnstrc-item-name",
        "product-price-attribute": "data-cnstrc-item-price",
        "product-link-class": "name-link",
        "product-link-anchor": '//*[@id="174b30c07ece67b84f916beead"]/div[3]/div[1]/a',
        "description-div": '//*[@id="pdpMain"]/div[4]/div/div[1]/div[2]/div/p[2]', 
                 
    },
    
    "https://www.valuecityfurniture.com/": 
    {
        "search": '//*[@id="ts-searchInput"]', 
        "product-grid": '//*[@id="page-container"]/bpc-app/div[1]/bpc-search-base/bpc-search-page-base/section[2]',
        "product-cards-tag": "product-card ng-star-inserted",
        "product-name-attribute": "",
        "product-price-class": "price-label",
        "product-link-class": "",
        "product-link-anchor": '',
        "description-div": '', 
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

    }
    }