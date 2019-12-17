import React, { PureComponent } from 'react'
import styles from './../Checkout/checkout.module.scss';
import ItemSelector from '../../Components/Checkout/ItemSelector/ItemSelector';
import BasketItem from '../../Components/Checkout/BasketItem/BasketItem';
import QuantitySelect from '../../Components/Checkout/ItemSelector/QuantitySelect';
import { groupedOptions } from './../../Components/Checkout/CheckoutCards/testData';
import { ReactComponent as Close } from './../../Assets/Images/Icons/x.svg';

export default class ReturnItems extends PureComponent {
  constructor(props) {
    super(props);
    this.state = {
      selectedTeam: null,
      checkoutFields: [{name: "", selectOptions: [], selectedQuantity: {value: null}}, {name: "", selectOptions: [], selectedQuantity: {value: null}}, {name: "", selectOptions: [], selectedQuantity: {value: null}}],
      basketHardwares: [],
      selectedHardware: null,
      teams: null}
    this.getSelectedHardware = this.getSelectedHardware.bind(this);
    this.changeQuantity = this.changeQuantity.bind(this);
    this.deleteCheckoutField = this.deleteCheckoutField.bind(this);
    fetch('http://ieee.utoronto.ca/makeuoft/api/teamscheckout')
      .then(response => response.json())
      .then(teams => this.setState({ teams }));
  }

  changeQuantity = (evt, index) => {
    this.setState(state => {
      const checkoutFields = state.checkoutFields.map((item, j) => {
        if (j === index) {
          item.selectedQuantity = evt
          return item;
        } else {
          return item;
        }
      });
      return { checkoutFields };
    })
  }

  getSelectedHardware(evt, index) {
    if (evt != null) {
      this.setState({selectedHardware: evt})
      this.setState(state => {
        const checkoutFields = state.checkoutFields.map((item, j) => {
          if (j === index) {
            item.selectOptions.length = 0;
            item.selectedQuantity = null;
            for (let i = 1; i < evt.stock + 1; i++) {
              item.selectOptions.push({value: i, label: i});
            }
            item.name = evt.label
            return item;
          } else {
            return item;
          }
        });
        return { checkoutFields};
      })
    };
  }

  selectTeam = teamValue => {
    this.setState({ selectedTeam: teamValue})
    console.log("WHICH TEAM IS IT???", teamValue);
  }

  addToBasket = index => {
    const { checkoutFields } = this.state;

    {checkoutFields[index].selectedQuantity &&
      this.setState(state => {
        let found = false;

        const basketHardwares = state.basketHardwares.map((item, j) => {
          if (j === index) {
            item.name = checkoutFields[index].name;
            item.selectedQuantity = checkoutFields[index].selectedQuantity.value;
            item.key = index;
            found = true;
            return item;
          } else {
            return item;
          }
        });
        if (!found) {
          basketHardwares.push({name: checkoutFields[index].name, selectedQuantity: checkoutFields[index].selectedQuantity.value, key: index})
        }
        return { basketHardwares };
      });
    }
  }

  deleteCheckoutField = indexL => {
    console.log("index", indexL);
    const { checkoutFields, basketHardwares } = this.state;
    // console.log("yoooooo")
    // checkoutFields.splice(index-1, 1);
    // basketHardwares.splice(index-1, 1);
    // console.log("index", index-1);
    // console.log("checkoutFields", checkoutFields);
    // console.log("basketHardwares", basketHardwares);

    this.setState(state => {
      const checkoutFields = state.checkoutFields.filter((item, j) => (indexL-1) !== j);
      return { checkoutFields };
    });
    this.setState(state => {
      const basketHardwares = state.basketHardwares.filter((item, j) => (indexL-1) !== j);
      return { basketHardwares };
    });

  }

  addField () {
    this.setState(state => {
      const checkoutFields = state.checkoutFields.concat({name: "", selectOptions: [], selectedQuantity: {value: null}});

      return {
        checkoutFields
      };
    });
  }

  sendRequestForCheckout () {
    // console.log("Team to checkout:", this.state.selectedTeam.value);
    // console.log("ITEMS TO DO:", this.state.basketHardwares);
    var itemList = [];
    for(var i=0; i<this.state.basketHardwares.length; i++){
      itemList.push({"name": this.state.basketHardwares[i].name,
                     "quantity":this.state.basketHardwares[i].selectedQuantity });
    }

    var data = {
      "team" : this.state.selectedTeam.value,
      "items" :  itemList
    }
    console.log("DATA", data);

    fetch('http://ieee.utoronto.ca/makeuoft/api/checkoutitems', {
      method: "POST",
      body:JSON.stringify(data)
    })
      .then(function(response) {
        console.log(response);
      })
      .then(function(data){
        console.log(data);
      });
  }

  render() {
    let componentField = [];
    let { checkoutFields, basketHardwares, selectedHardware, teams } = this.state;
    const basketEmpty = (basketHardwares === null);
    const teamsDataRecevied = (teams === null);

    for (var i = 0; i < checkoutFields.length; i ++) {
      componentField.push(
        <div className={styles.checkoutTableDivItem} fieldIndex={i}>
          <Close className={styles.checkoutTableDivItemClose} onClick={() => this.deleteCheckoutField(i)}/>
          <ItemSelector type="component"
            options={groupedOptions}
            selectItem={this.getSelectedHardware}
            fieldIndex={i} />

          <QuantitySelect
            selectQuantity={this.addToBasket}
            fieldIndex={i}
            onChange = {this.changeQuantity}
            selectedHardware={selectedHardware}
            selectedValue={checkoutFields[i].selectedQuantity}
            options={checkoutFields[i].selectOptions} />
        </div>
      );
    };

    return (
      <div className={styles.checkout}>
        <div className={styles.checkoutDiv}>
          <div className={styles.checkoutList}>
            <h2>Team Information</h2>
            <div className={styles.checkoutTable}>
              <p>Team Number</p>
            </div>

            <div className={styles.checkoutTableDiv} style={{marginBottom: 40}}>
              <div className={styles.checkoutTableDivItem}>
                {teamsDataRecevied ? (
                  <p className={styles.inventoryListLoading}>Loading...</p>
                ) : (
                    <ItemSelector type="team"
                      selectTeam={this.selectTeam}
                      options={teams} />
                )}
              </div>
            </div>

            <h2>Return Items</h2>
            <div className={styles.checkoutTable}>
              <p>Component</p>
              <p>Quantity</p>
            </div>
            <div className={styles.checkoutTableDiv}>
              {componentField}

              <button className={styles.btnOutline} onClick={()=>this.addField()}>Add Component</button>
            </div>
          </div>
        </div>

        <div className={styles.checkoutDiv}>
          <div className={styles.checkoutBasket}>
            <h2>Returned Items</h2>
            <div className={styles.checkoutTable}>
              <p>Component</p>
              <p>Quantity</p>
            </div>

            <div className={styles.checkoutTableDiv}>
              <div className={styles.checkoutTableDivBasketItems}>
                {!basketEmpty &&
                  basketHardwares.map((item, i) => {
                    return (
                      <BasketItem component={item.name} quantity={item.selectedQuantity} key={item.key} />
                    )
                  }
                )}
              </div>
              <div className={styles.checkoutTableDivBasketConfirm}>
                {/* <p>{selectedTeam ? `Confirm this is with ${selectedTeam.label}` : ""}</p> */}
                <button className={styles.btnFilled} onClick={()=>this.sendRequestForCheckout()} type={"submit"}>Submit</button>
                {/* {console.log("basket", basketHardwares)} */}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
