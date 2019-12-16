import React, { PureComponent } from 'react'
import styles from './teamOverviewAccordion.module.scss';
import { AccordionItem, AccordionItemHeading, AccordionItemPanel, AccordionItemButton } from 'react-accessible-accordion';

export default class TeamOverviewAccordion extends PureComponent {
    render() {
        let { children, heading} = this.props;

        return (
            <AccordionItem className={styles['accordion__item']} uuid={"checkout"}>
              <AccordionItemHeading>
                  <AccordionItemButton className={styles['accordion__button']}>
                      {heading}
                  </AccordionItemButton>
              </AccordionItemHeading>
              <AccordionItemPanel className={styles['accordion__panel']}>
                  {children}
              </AccordionItemPanel>
          </AccordionItem>
        )
    }
}
